import json
import os
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from speedy.core.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software

from speedy.net.accounts.tests.test_factories import UserFactory
from ..models import Image


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class UploadViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        upload_file = tempfile.NamedTemporaryFile()
        upload_file.file.write(b'this is a file')
        upload_file.file.seek(0)
        self.data = {
            'file': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        self.upload_file = upload_file
        self.page_url = '/uploads/upload/'

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url, self.data)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_upload_file(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.post(self.page_url, self.data)
        self.assertEqual(first=r.status_code, second=200)
        json_response = json.loads(r.content.decode())
        self.assertEqual(first=len(json_response['files'][0]['uuid']), second=20)
        self.assertEqual(first=json_response['files'][0]['name'], second=os.path.basename(self.upload_file.name))
        self.assertEqual(first=json_response['files'][0]['type'], second='image')
        self.assertEqual(first=Image.objects.count(), second=1)
        image = Image.objects.first()
        assert isinstance(image, Image)
        self.assertEqual(first=str(image.id), second=json_response['files'][0]['uuid'])
        self.assertEqual(first=image.basename, second=json_response['files'][0]['name'])
        self.assertEqual(first=image.size, second=14)
        self.assertEqual(first=image.owner_id, second=self.user.id)