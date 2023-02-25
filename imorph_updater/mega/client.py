import binascii
import json
import logging
import math
import os
import random
import re
import shutil
import tempfile
import typing as T
import uuid
from pathlib import Path

import requests
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util import Counter

from .encrypt import (
    AESType,
    a32_to_base64,
    a32_to_str,
    base64_to_a32,
    base64_url_decode,
    base64_url_encode,
    decrypt_attr,
    decrypt_key,
    encrypt_key,
    get_chunks,
    modular_inverse,
    mpi_to_int,
    str_to_a32,
)

logger = logging.getLogger(__name__)


class Mega:
    def __init__(self) -> None:
        self.schema = "https"
        self.domain = "mega.co.nz"
        self.timeout = 160  # max secs to wait for resp from api requests
        self.sid = None
        self.sequence_num = random.randint(0, 0xFFFFFFFF)
        self.request_id = str(uuid.uuid4())

    def login(self) -> T.Self:
        self.login_anonymous()
        return self

    def login_anonymous(self) -> None:
        master_key = [random.randint(0, 0xFFFFFFFF)] * 4
        password_key = [random.randint(0, 0xFFFFFFFF)] * 4
        session_self_challenge = [random.randint(0, 0xFFFFFFFF)] * 4
        z = encrypt_key(master_key, password_key)
        user = self._api_request(
            {
                "a": "up",
                "k": a32_to_base64(z),
                "ts": base64_url_encode(
                    a32_to_str(session_self_challenge)
                    + a32_to_str(encrypt_key(session_self_challenge, master_key))
                ),
            }
        )

        resp = self._api_request({"a": "us", "user": user})
        if isinstance(resp, int):
            raise Exception(f"Incorrect response for login: {resp}")
        self._login_process(resp, password_key)

    def _api_request(self, data: dict) -> dict:
        params = {"id": self.sequence_num}
        self.sequence_num += 1

        data = [data]

        if self.sid:
            params.update({"sid": self.sid})

        url = f"{self.schema}://g.api.{self.domain}/cs"
        response = requests.post(
            url,
            params=params,
            data=json.dumps(data),
            timeout=self.timeout,
        )
        json_resp = json.loads(response.text)
        try:
            if isinstance(json_resp, list):
                int_resp = json_resp[0] if isinstance(json_resp[0], int) else None
            elif isinstance(json_resp, int):
                int_resp = json_resp
        except IndexError:
            int_resp = None
        if int_resp is not None:
            if int_resp == 0:
                return int_resp
            if int_resp == -3:
                msg = "Request failed, retrying"
                raise RuntimeError(msg)
            raise Exception(int_resp)
        return json_resp[0]

    def _login_process(self, resp: dict, password: AESType) -> None:
        encrypted_master_key = base64_to_a32(resp["k"])
        self.master_key = decrypt_key(encrypted_master_key, password)
        if "tsid" in resp:
            tsid = base64_url_decode(resp["tsid"])
            key_encrypted = a32_to_str(
                encrypt_key(str_to_a32(tsid[:16]), self.master_key)
            )
            if key_encrypted == tsid[-16:]:
                self.sid = resp["tsid"]
        elif "csid" in resp:
            encrypted_rsa_private_key = base64_to_a32(resp["privk"])
            rsa_private_key = decrypt_key(encrypted_rsa_private_key, self.master_key)

            private_key = a32_to_str(rsa_private_key)
            # The private_key contains 4 MPI integers concatenated together.
            rsa_private_key = [0, 0, 0, 0]
            for i in range(4):
                # An MPI integer has a 2-byte header which describes the number
                # of bits in the integer.
                bitlength = (private_key[0] * 256) + private_key[1]
                bytelength = math.ceil(bitlength / 8)
                # Add 2 bytes to accommodate the MPI header
                bytelength += 2
                rsa_private_key[i] = mpi_to_int(private_key[:bytelength])
                private_key = private_key[bytelength:]

            first_factor_p = rsa_private_key[0]
            second_factor_q = rsa_private_key[1]
            private_exponent_d = rsa_private_key[2]
            # In MEGA's webclient javascript, they assign [3] to a variable
            # called u, but I do not see how it corresponds to pycryptodome's
            # RSA.construct and it does not seem to be necessary.
            rsa_modulus_n = first_factor_p * second_factor_q
            phi = (first_factor_p - 1) * (second_factor_q - 1)
            public_exponent_e = modular_inverse(private_exponent_d, phi)

            rsa_components = (
                rsa_modulus_n,
                public_exponent_e,
                private_exponent_d,
                first_factor_p,
                second_factor_q,
            )
            rsa_decrypter = RSA.construct(rsa_components)

            encrypted_sid = mpi_to_int(base64_url_decode(resp["csid"]))

            sid = "%x" % rsa_decrypter._decrypt(encrypted_sid)
            sid = binascii.unhexlify("0" + sid if len(sid) % 2 else sid)
            self.sid = base64_url_encode(sid[:43])

    def download_url(
        self,
        url: str,
        dest_path: T.Optional[Path] = None,
        dest_filename: T.Optional[Path] = None,
    ) -> Path:
        """
        Download a file by it's public url
        """
        file_id, file_key = self._parse_url(url).split("!")
        return self._download_file(
            file_handle=file_id,
            file_key=file_key,
            dest_path=dest_path,
            dest_filename=dest_filename,
            is_public=True,
        )

    def _download_file(
        self,
        file_handle: str,
        file_key: str,
        dest_path: T.Optional[Path] = None,
        dest_filename: T.Optional[Path] = None,
        is_public: bool = False,
    ) -> Path:
        if is_public:
            file_key = base64_to_a32(file_key)
            file_data = self._api_request({"a": "g", "g": 1, "p": file_handle})
        else:
            file_data = self._api_request({"a": "g", "g": 1, "n": file_handle})

        k = (
            file_key[0] ^ file_key[4],
            file_key[1] ^ file_key[5],
            file_key[2] ^ file_key[6],
            file_key[3] ^ file_key[7],
        )
        iv = file_key[4:6] + (0, 0)
        meta_mac = file_key[6:8]

        # Seems to happens sometime... When this occurs, files are
        # inaccessible also in the official also in the official web app.
        # Strangely, files can come back later.
        if "g" not in file_data:
            raise Exception("File not accessible anymore")
        file_url = file_data["g"]
        file_size = file_data["s"]
        attribs = base64_url_decode(file_data["at"])
        attribs = decrypt_attr(attribs, k)

        if dest_filename is not None:
            file_name = dest_filename
        else:
            file_name = attribs["n"]

        input_file = requests.get(file_url, stream=True).raw

        if dest_path is None:
            dest_path = ""
        else:
            dest_path += "/"

        with tempfile.NamedTemporaryFile(
            mode="w+b", prefix="megapy_", delete=False
        ) as temp_output_file:
            k_str = a32_to_str(k)
            counter = Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64)
            aes = AES.new(k_str, AES.MODE_CTR, counter=counter)

            mac_str = "\0" * 16
            mac_encryptor = AES.new(k_str, AES.MODE_CBC, mac_str.encode("utf8"))
            iv_str = a32_to_str([iv[0], iv[1], iv[0], iv[1]])

            for _, chunk_size in get_chunks(file_size):
                chunk = input_file.read(chunk_size)
                chunk = aes.decrypt(chunk)
                temp_output_file.write(chunk)

                encryptor = AES.new(k_str, AES.MODE_CBC, iv_str)
                for i in range(0, len(chunk) - 16, 16):
                    block = chunk[i : i + 16]
                    encryptor.encrypt(block)

                # fix for files under 16 bytes failing
                if file_size > 16:
                    i += 16
                else:
                    i = 0

                block = chunk[i : i + 16]
                if len(block) % 16:
                    block += b"\0" * (16 - (len(block) % 16))
                mac_str = mac_encryptor.encrypt(encryptor.encrypt(block))

                file_info = os.stat(temp_output_file.name)
                logger.info("%s of %s downloaded", file_info.st_size, file_size)
            file_mac = str_to_a32(mac_str)
            # check mac integrity
            if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
                raise ValueError("Mismatched mac")
            output_path = Path(dest_path + file_name)
            shutil.move(temp_output_file.name, output_path)
            return output_path

    def _parse_url(self, url: str) -> str:
        """Parse file id and key from url."""
        if "/file/" in url:
            # V2 URL structure
            url = url.replace(" ", "")
            file_id = re.findall(r"\W\w\w\w\w\w\w\w\w\W", url)[0][1:-1]
            id_index = re.search(file_id, url).end()
            key = url[id_index + 1 :]
            return f"{file_id}!{key}"
        elif "!" in url:
            # V1 URL structure
            match = re.findall(r"/#!(.*)", url)
            path = match[0]
            return path
        else:
            raise Exception("Url key missing")
