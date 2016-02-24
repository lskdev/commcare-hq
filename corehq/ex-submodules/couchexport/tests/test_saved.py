# coding=utf-8
import datetime
import uuid

from django.test import TestCase

from corehq.apps.export.export import _get_cached_export_and_delete_copies
from corehq.apps.export.models.new import CachedExport, _ATTACHEMENT_NAME
from couchexport.groupexports import get_saved_export_and_delete_copies
from couchexport.models import SavedBasicExport, ExportConfiguration


class CachedExportTest(TestCase):

    def test_file_save_and_load(self):
        payload = 'something small and simple'
        saved = CachedExport()
        saved.save()
        saved.set_payload(payload)
        self.assertEqual(payload, saved.get_payload())

    def test_get_cached_export_and_delete_copies_missing(self):
        self.assertEqual(None, _get_cached_export_and_delete_copies(uuid.uuid4().hex))

    def test_get_saved_and_delete_copies_single(self):
        export_instance_id = uuid.uuid4().hex
        saved_export = CachedExport(export_instance_id=export_instance_id)
        saved_export.save()
        self.assertEqual(saved_export._id, _get_cached_export_and_delete_copies(export_instance_id)._id)

    def test_get_saved_and_delete_copies_multiple(self):
        export_instance_id = uuid.uuid4().hex
        # make three exports with the last one being the most recently updated
        timestamp = datetime.datetime.utcnow()
        for i in range(3):
            saved_export = CachedExport(export_instance_id=export_instance_id,
                                        last_updated=timestamp + datetime.timedelta(days=i))
            saved_export.save()

        self.assertEqual(3, len(CachedExport.by_export_instance_id(export_instance_id)))
        chosen_one = _get_cached_export_and_delete_copies(export_instance_id)
        # this relies on the variable being set last in the loop which is a bit unintuitive
        self.assertEqual(saved_export._id, chosen_one._id)
        saved_after_deletion = CachedExport.by_export_instance_id(export_instance_id)
        self.assertEqual(1, len(saved_after_deletion))
        self.assertEqual(chosen_one._id, saved_after_deletion[0]._id)

    def test_save_basic_export_to_blobdb(self):
        export_instance_id = uuid.uuid4().hex
        saved_export = CachedExport(export_instance_id=export_instance_id)
        saved_export.save()
        saved_export.set_payload("content")
        self.assertTrue(saved_export.has_file())
        self.assertIn(_ATTACHEMENT_NAME, saved_export.external_blobs)
        self.assertEqual(saved_export.size, 7)
        with saved_export.get_payload(stream=True) as fh:
            self.assertEqual(fh.read(), "content")


class SavedBasicExportTest(TestCase):

    def test_file_save_and_load(self):
        payload = 'something small and simple'
        for name in ['normal', u'हिंदी', None]:
            saved = SavedBasicExport(configuration=_mk_config(name))
            saved.save()
            saved.set_payload(payload)
            self.assertEqual(payload, saved.get_payload())

    def test_get_by_index(self):
        index = ['some', 'index']
        saved_export = SavedBasicExport(configuration=_mk_config(index=index))
        saved_export.save()
        back = SavedBasicExport.by_index(index)
        self.assertEqual(1, len(back))
        self.assertEqual(saved_export._id, back[0]._id)

    def test_get_saved_and_delete_copies_missing(self):
        self.assertEqual(None, get_saved_export_and_delete_copies(['missing', 'index']))

    def test_get_saved_and_delete_copies_single(self):
        index = ['single']
        saved_export = SavedBasicExport(configuration=_mk_config(index=index))
        saved_export.save()
        self.assertEqual(saved_export._id, get_saved_export_and_delete_copies(index)._id)

    def test_get_saved_and_delete_copies_multiple(self):
        index = ['multiple']
        # make three exports with the last one being the most recently updated
        timestamp = datetime.datetime.utcnow()
        for i in range(3):
            saved_export = SavedBasicExport(configuration=_mk_config(index=index),
                                            last_updated=timestamp + datetime.timedelta(days=i))
            saved_export.save()

        self.assertEqual(3, len(SavedBasicExport.by_index(index)))
        chosen_one = get_saved_export_and_delete_copies(index)
        # this relies on the variable being set last in the loop which is a bit unintuitive
        self.assertEqual(saved_export._id, chosen_one._id)
        saved_after_deletion = SavedBasicExport.by_index(index)
        self.assertEqual(1, len(saved_after_deletion))
        self.assertEqual(chosen_one._id, saved_after_deletion[0]._id)

    def test_save_basic_export_to_blobdb(self):
        index = ['single']
        saved_export = SavedBasicExport(configuration=_mk_config(index=index))
        saved_export.save()
        saved_export.set_payload("content")
        name = saved_export.get_attachment_name()
        self.assertTrue(saved_export.has_file())
        self.assertIn(name, saved_export.external_blobs)
        self.assertEqual(saved_export.size, 7)
        with saved_export.get_payload(stream=True) as fh:
            self.assertEqual(fh.read(), "content")


def _mk_config(name='some export name', index='dummy_index'):
    return ExportConfiguration(index=index, name=name, format='xlsx')
