# HoSoInWorker

Worker Windows de doc email qua IMAP, tai attachment tu mailbox/label con, dua vao `C:/ho_so_in/chua_in`, giai nen file archive/phong nen ho tro boi Python, in file hop le, roi chuyen file da in sang `C:/ho_so_in/da_in`.

## Yeu cau

- Windows co Python 3.11+.
- Tai khoan email bat IMAP.
- Neu dung Gmail, can App Password.
- May da cai app mac dinh co the in cac dinh dang trong `ALLOWED_EXTENSIONS`.

## Cau hinh

1. Copy `.env.example` thanh `.env`.
2. Dien cac bien email:

```env
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_IMAP_USER=your-email@gmail.com
EMAIL_IMAP_PASSWORD=your-app-password
# Case phong
EMAIL_IMAP_MAILBOX=ho_so/phong/ho_so_in_phong
EMAIL_DONE_MAILBOX=ho_so/phong/ho_so_da_in_phong

# Case hai
# EMAIL_IMAP_MAILBOX=ho_so/hai/ho_so_in_hai
# EMAIL_DONE_MAILBOX=ho_so/hai/ho_so_da_in_hai
EMAIL_IMAP_TIMEOUT_SECONDS=30
EMAIL_SEARCH_CRITERIA=ALL
POLL_INTERVAL_SECONDS=600
```

Mac dinh thu muc xu ly:

```env
PENDING_DIR=C:/ho_so_in/chua_in
PRINTED_DIR=C:/ho_so_in/da_in
```

Neu muon in bang may in cu the, dien `PRINTER_NAME`. Neu de trong, Windows se dung may in mac dinh.

De in PDF on dinh, nen cai SumatraPDF va dien duong dan:

```env
PDF_PRINT_APP_PATH=C:/Program Files/SumatraPDF/SumatraPDF.exe
```

Neu muon chi in mot so trang trong PDF, them:

```env
PRINT_PAGES=1-3,5,last
```

Gia tri nay tuong ung voi settings cua SumatraPDF, vi du:

- `1-3,5,last` in trang 1 den 3, trang 5 va trang cuoi
- `odd` in trang le
- `even` in trang chan
- `-2--1` in 2 trang cuoi

Luu y: worker da co rule tu dong theo ten file PDF:

- `HAN{han_code}.pdf` se chi in trang 1
- `ApplyForm_{code}.pdf` se in trang 1 va 7, dong thoi in 2 mat

Neu file khong khop 2 rule nay thi worker moi dung `PRINT_PAGES` va `PRINT_DUPLEX` lam fallback.

Neu muon bat in 2 mat cho PDF, them:

```env
PRINT_DUPLEX=long
```

Gia tri ho tro:

- `long` hoac `duplexlong` cho lat theo canh dai
- `short` hoac `duplexshort` cho lat theo canh ngan
- `simplex` de ep in 1 mat
- `off` de bo qua cau hinh nay

## Chay thu

```powershell
python .\src\main.py
```

Log nam o:

```text
C:/ho_so_in/worker.log
```

## Build exe

```powershell
.\scripts\build.ps1
```

File exe se nam tai:

```text
dist/HoSoInWorker.exe
```

## Cai vao Startup Windows

Sau khi build:

```powershell
.\scripts\install-startup.ps1
```

Script tao shortcut trong Startup folder cua user hien tai. Khi Windows dang nhap, worker se tu chay, doc file `.env` trong project nay, va quet email moi moi 10 phut neu `POLL_INTERVAL_SECONDS=600`.

Go khoi Startup:

```powershell
.\scripts\uninstall-startup.ps1
```

## Luong xu ly

1. Doc email tu IMAP theo `.env`.
2. Select mailbox/label `EMAIL_IMAP_MAILBOX`, vi du `ho_so/phong/ho_so_in_phong`.
3. Search email theo `EMAIL_SEARCH_CRITERIA`, mac dinh `ALL`.
4. Tai attachment xuong `C:/ho_so_in/chua_in`.
5. Chuyen email da tai attachment sang `EMAIL_DONE_MAILBOX` de tranh quet lai.
6. Xoa noi dung `C:/ho_so_in/da_in` khi worker khoi dong.
7. Kiem tra `chua_in`: file `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2`, `.tar.xz`, `.txz` se duoc giai nen, folder/pdf/file hop le duoc giu de in.
8. In tat ca file co extension trong `ALLOWED_EXTENSIONS`.
9. Chuyen file da in sang `C:/ho_so_in/da_in`.

## Luu y

- `DELETE_PRINTED_DIR_ON_START=true` se xoa noi dung `da_in` moi lan worker khoi dong.
- `DELETE_PRINTED_DIR_EACH_CYCLE=false` de tranh xoa file vua in lien tuc trong luc worker dang chay.
- `EMAIL_DONE_MAILBOX` nen dung dung full IMAP path tuong ung voi `EMAIL_IMAP_MAILBOX`, vi du `ho_so/phong/ho_so_da_in_phong`.
- `POLL_INTERVAL_SECONDS=600` nghia la worker quet nhan nguon moi 10 phut.
- `PDF_PRINT_APP_PATH` nen tro toi `SumatraPDF.exe` neu Windows bao loi khong co app nao gan voi thao tac in PDF.
- `PRINT_PAGES` chi ap dung cho file PDF khi in qua SumatraPDF.
- `PRINT_DUPLEX` chi ap dung on dinh cho file PDF khi in qua SumatraPDF; voi file khac, worker van in theo app/mac dinh cua may in.
- Neu in PDF khong hoat dong, cai SumatraPDF/Adobe Reader va dat app mac dinh cho `.pdf`.
