# Module 16: team chat and announcements

Every currently authorised community member can send text, links, replies, files and single-choice polls. Conversations persist in the database across logout and restart. The chat refreshes every three seconds, loads older messages in batches of 40 and retries network failures without creating duplicate messages. An uncertain send freezes its original draft until the retry succeeds, preventing accidental edits from being lost.

Photos display inline. Audio and video use native playback controls with authenticated byte-range support. A searchable, paginated Media, files & links library retains the attachments and links in the conversation. Downloads always recheck current community membership and agreement clearance; uploaded files have no public media route.

Supported files: JPEG/PNG/GIF/WebP; PDF, Office files, TXT/CSV/JSON/ZIP; MP3/WAV/OGG/M4A/AAC/FLAC; MP4/MOV/WebM. Maximum 5 attachments per message, 25 MB each, 60 MB total. Files undergo format checks, images are limited to 40 million pixels, PDFs to 500 pages and archive metadata to 150 MB unpacked. Format checks are not antivirus scanning. Browser codec support determines which media play inline; downloads remain available.

Voice notes use the browser microphone after user permission, stop after two minutes and are attached for explicit sending. A recording can be replaced or removed before sending. Physical microphone capture has not been tested on the user's device; WAV attachment delivery and playback range requests are tested.

Polls support 2–10 distinct options, one current vote per member, changing a vote, visible totals and closing by the poll creator or team managers. Mentor and appointed leader can publish and revise announcements, with revision history, stale-edit protection and persistent in-app notifications to eligible teammates.

Open My Projects, then the project's community, then Internal Chat or Announcements. Chat is a private project group experience with WhatsApp-inspired styling; it does not implement end-to-end encryption, calls, typing indicators or delivery/read receipts. Task assignment and review remain Module 17.

Validation: all 134 Django tests passed, including eight new chat/announcement tests covering permission revocation, cross-record denial, CSRF, escaping, file cleanup on failure, idempotent sends, pagination, votes, downloads/ranges and announcement revisions. An isolated browser demo verified message sending, poll creation/voting, polling and the media library without adding records to the live project database.
