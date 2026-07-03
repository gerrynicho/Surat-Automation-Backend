from pydantic import BaseModel, field_validator
from typing import Literal

VALID_BULAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


class Participant(BaseModel):
    nama: str
    nrp: str
    jurusan: str


class SuratMetadata(BaseModel):
    bulan: str
    tanggal_pengajuan: str
    perihal: str
    kode: str

    @field_validator("bulan")
    @classmethod
    def validate_bulan(cls, v: str) -> str:
        stripped = v.strip()
        if stripped not in VALID_BULAN:
            raise ValueError(f"bulan must be one of: {', '.join(VALID_BULAN)}")
        return stripped


class SuratData(BaseModel):
    TUJUAN: str
    ITSORNO: bool
    NAMAKEGIATAN: str
    HARITANGGAL: str
    ACARAYANGMINTAIZIN: str


class CreateSuratRequest(BaseModel):
    nama_kepengurusan: str
    new_name: str
    metadata: SuratMetadata
    data: SuratData
    participants: list[Participant]


class FileActionRequest(BaseModel):
    nama_kepengurusan: str
    nama_file: str
