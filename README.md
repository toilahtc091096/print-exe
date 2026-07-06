# HoSoInWorker

Worker Windows de doc email qua IMAP, tai attachment tu mailbox/label `ho_so_in`, dua vao `C:/ho_so_in/chua_in`, giai nen file zip, in file hop le, roi chuyen file da in sang `C:/ho_so_in/da_in`.

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
EMAIL_IMAP_MAILBOX=ho_so_in
EMAIL_DONE_MAILBOX=ho_so_da_in
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
2. Select mailbox/label `EMAIL_IMAP_MAILBOX`, mac dinh `ho_so_in`.
3. Search email theo `EMAIL_SEARCH_CRITERIA`, mac dinh `ALL`.
4. Tai attachment xuong `C:/ho_so_in/chua_in`.
5. Chuyen email da tai attachment sang `EMAIL_DONE_MAILBOX` de tranh quet lai.
6. Xoa noi dung `C:/ho_so_in/da_in` khi worker khoi dong.
7. Kiem tra `chua_in`: file `.zip` se duoc giai nen, folder/pdf/file hop le duoc giu de in.
8. In tat ca file co extension trong `ALLOWED_EXTENSIONS`.
9. Chuyen file da in sang `C:/ho_so_in/da_in`.

## Luu y

- `DELETE_PRINTED_DIR_ON_START=true` se xoa noi dung `da_in` moi lan worker khoi dong.
- `DELETE_PRINTED_DIR_EACH_CYCLE=false` de tranh xoa file vua in lien tuc trong luc worker dang chay.
- `EMAIL_DONE_MAILBOX=ho_so_da_in` la nhan/mailbox dich sau khi da tai attachment. De trong bien nay neu khong muon chuyen email.
- `POLL_INTERVAL_SECONDS=600` nghia la worker quet nhan nguon moi 10 phut.
- `PDF_PRINT_APP_PATH` nen tro toi `SumatraPDF.exe` neu Windows bao loi khong co app nao gan voi thao tac in PDF.
- Neu in PDF khong hoat dong, cai SumatraPDF/Adobe Reader va dat app mac dinh cho `.pdf`.
