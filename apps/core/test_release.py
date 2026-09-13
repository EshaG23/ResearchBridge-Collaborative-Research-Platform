import json,sqlite3,tempfile
from contextlib import closing
from pathlib import Path
from io import StringIO
from django.test import SimpleTestCase,override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from apps.core.backup import backup,restore,verify

class BackupTests(SimpleTestCase):
    def test_backup_restore_integrity_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);data=root/'data';data.mkdir();(data/'uploads').mkdir();(data/'uploads'/'evidence.txt').write_text('preserved evidence');(data/'.development-secret').write_text('test secret')
            with closing(sqlite3.connect(data/'db.sqlite3')) as db:db.execute('CREATE TABLE proof (value TEXT)');db.execute('INSERT INTO proof VALUES (?)',('saved record',));db.commit()
            with override_settings(DATA_DIR=data):
                with self.assertRaises(CommandError):call_command('backup_workspace',str(root/'backup'),stdout=StringIO())
                call_command('backup_workspace',str(root/'backup'),writers_stopped=True,stdout=StringIO())
            call_command('restore_workspace',str(root/'backup'),str(root/'restored'),stdout=StringIO())
            self.assertEqual((root/'restored'/'uploads'/'evidence.txt').read_text(),'preserved evidence')
            with closing(sqlite3.connect(root/'restored'/'db.sqlite3')) as db:self.assertEqual(db.execute('SELECT value FROM proof').fetchone()[0],'saved record')
            with self.assertRaises(ValueError):restore(root/'backup',root/'restored')
            (root/'backup'/'uploads'/'evidence.txt').write_text('changed')
            with self.assertRaises(ValueError):verify(root/'backup')
    def test_manifest_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'manifest.json').write_text(json.dumps({'format':1,'files':{'../outside':'x','db.sqlite3':'x'}}))
            with self.assertRaises(ValueError):verify(root)
