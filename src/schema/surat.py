from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

VALID_BULAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

# Trimmed and never empty. The preview is rendered without going through the
# GAS payload validation, so the same rules are enforced here.
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Participant(BaseModel):
    nama: NonEmptyStr
    nrp: NonEmptyStr
    jurusan: NonEmptyStr


class SuratMetadata(BaseModel):
    bulan: str
    tanggal_pengajuan: NonEmptyStr
    perihal: NonEmptyStr
    kode: NonEmptyStr

    @field_validator("bulan")
    @classmethod
    def validate_bulan(cls, v: str) -> str:
        stripped = v.strip()
        if stripped not in VALID_BULAN:
            raise ValueError(f"bulan must be one of: {', '.join(VALID_BULAN)}")
        return stripped

    @field_validator("kode")
    @classmethod
    def uppercase_kode(cls, v: str) -> str:
        return v.upper()


class SuratData(BaseModel):
    TUJUAN: NonEmptyStr
    ITSORNO: bool
    NAMAKEGIATAN: NonEmptyStr
    HARITANGGAL: NonEmptyStr
    ACARAYANGMINTAIZIN: NonEmptyStr


class CreateSuratRequest(BaseModel):
    nama_kepengurusan: NonEmptyStr
    new_name: NonEmptyStr
    metadata: SuratMetadata
    data: SuratData
    participants: list[Participant] = Field(min_length=1)


class PreviewSuratResponse(BaseModel):
    # Predicted number: nothing is written to the spreadsheet until finalize.
    nomor_surat: str
    pdf_base64: str
    warnings: list[str]
    # True when finalize would be refused (Ketua data, TTD or stempel missing).
    blocked: bool


class FinalizeSuratResponse(BaseModel):
    success: bool
    nomor_surat: str
    file_name: str
    url: str
