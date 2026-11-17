from typing import Annotated, Literal

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
    """Returned when a new letter is finalized and when an existing one is edited."""

    success: bool
    # Running number (column NO. of the arsip). The dashboard addresses a letter by it.
    nomor: int | None = None
    nomor_surat: str
    file_name: str
    url: str


class SuratListItem(BaseModel):
    """One row of the arsip, as the Arsip Surat dashboard lists it."""

    # 0 when the arsip row has no valid number: such a row can only be looked at.
    nomor: int
    nomor_surat: str
    bulan: str
    tanggal: str
    perihal: str
    kode: str
    status: Literal["aktif", "dibatalkan"]
    # False for letters the app has no data of (made before the dashboard existed,
    # or typed into the spreadsheet by hand) and for cancelled ones.
    editable: bool
    file_name: str
    url: str
    updated_at: str


class SuratListResponse(BaseModel):
    surat: list[SuratListItem]


class SuratDetailResponse(SuratListItem):
    # The data the letter was built from; None when the app does not have it.
    form: CreateSuratRequest | None
    # None when the PDF is no longer in Berkas Keluar.
    pdf_base64: str | None


class DeleteSuratResponse(BaseModel):
    success: bool
    nomor: int
    nomor_surat: str
    # "removed": it was the latest letter, so its number is free again.
    # "cancelled": the arsip row is kept and marked, so the number stays taken.
    mode: Literal["removed", "cancelled"]
