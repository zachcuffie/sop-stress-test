# Monthly Backup Restore Test

Owner: Operations Lead (backup: Office Manager)
Version 3, reviewed every six months or after any change to the backup service.

## 1. Purpose and scope
Prove each month that the file-server backup can be restored. This covers the company file server only. Laptops are out of scope and are covered by the Laptop Backup SOP held in the Operations folder of the shared drive.

## 2. Schedule and trigger
The Operations Lead runs this test on the first Tuesday of each month. If the Operations Lead is absent that week, the Office Manager runs it. If neither can run it that week, the Operations Lead runs it within the following five working days and notes the delay in the test log.

## 3. Prerequisites
- Restore permission in the backup service console (held by the Operations Lead and the Office Manager).
- The empty test folder "RestoreTest" on the file server.
- The test log spreadsheet "Restore Test Log" in the Operations folder.

## 4. Procedure
1. In the backup service console, choose the most recent nightly backup.
2. Pick three files: one from Projects, one from Operations and one from Marketing. Choose different files each month and record their names.
3. Restore the three files into the RestoreTest folder, not to their original location.
4. Open each restored file and confirm it opens and that its last-modified date matches the date shown for that file in the backup console.
5. Delete the restored files from RestoreTest.
6. Record in the Restore Test Log: date, who ran it, backup date used, file names, and pass or fail for each file.

## 5. If the test fails
1. Run the restore once more for any failed file.
2. If it fails again, record "fail" in the log and email the Operations Lead and the Managing Director the same day with the file names and the error shown.
3. The Operations Lead opens a support case with the backup provider the same day and records the case number in the log.
4. Until a restore succeeds, the Operations Lead checks each morning that the nightly backup job completed and records the result in the log.
5. The test counts as complete only when all three files restore successfully; the date of the successful restore is recorded.

## 6. Records
The Restore Test Log is kept for the life of the backup service plus one year. The Managing Director reviews the log every quarter and initials the review row.
