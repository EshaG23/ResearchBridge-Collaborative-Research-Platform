# Demo login accounts

All accounts use initial password **ResearchDemo!2026**. Local Forgot Password OTP: **123456**. These are fictional demo accounts.

| Role | Email | Department |
|---|---|---|
| Student | student1@rbunagpur.in | CSE |
| Student | student2@rbunagpur.in | AIML |
| Student | student3@rbunagpur.in | AIDS |
| Student | student4@rknec.in | EE |
| Student | student5@rknec.in | MECH |
| Teacher | teacher1@rbunagpur.in | CSE |
| Teacher | teacher2@rbunagpur.in | AIML |
| Teacher | teacher3@rbunagpur.in | AIDS |
| Teacher | teacher4@rknec.in | EE |
| Teacher | teacher5@rknec.in | MECH |

All 10 profiles start incomplete. Names, roles and departments come from the university demo roster; phone, skills, research interests, student year/availability and resume must be completed after login. Teachers are university-approved but still need to complete their profiles.

Passwords are hashed in the database. JSON initial passwords are demo setup data; changing a password updates the database. Re-importing the roster never resets an existing password.

## Demonstrating mentor matching

Both students and teachers must log in and complete their own profiles. Roster import creates approved login accounts with basic name and department data; it does not complete profiles.

For a 100-score example, first log in as Teacher 1 and complete the teacher profile with department **CSE**, research interest **Artificial intelligence**, and skills **Python**, **Data analysis**, **Statistics**, along with the other required fields. Then log in as a student, complete the student profile and create an idea using those same department, domain and skill tags.

This gives 50 points for research interest, 20 for department and 30 for matching every requested skill. Incomplete teacher profiles are not eligible for recommendations. Scores depend on the profiles users actually submit.

## Side-by-side demo accounts

Open http://127.0.0.1:8000/accounts/demo-session/ for each additional account, or click **Open another account** on the login page or demo banner. Each new tab has an independent session and CSRF token, with the signed-in email shown in its banner. Keep using the links inside that tab; refreshing retains its account. Logging out affects only that session. Duplicate tabs of the same session URL intentionally share that account; use the button to open a different account. All sessions share project data, chat and polls under the usual permissions. This feature is only available in local demo mode.
