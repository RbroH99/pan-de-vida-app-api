"""
Test for the models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import (
    MedClass,
    MedicinePresentation,
    Medicine,
    Note,
    Contact,
    PhoneNumber,
    WorkingSite,
)

UserProfile = get_user_model()


class ModelTests(TestCase):
    """Test models."""

    def test_user_profile(self):
        """Test creating user profile in the API."""
        email = 'userprofile@example.com'
        id = 1
        user = UserProfile.objects.create_user(id=id, email=email)

        self.assertEqual(str(user), email)

    def test_create_medclass(self):
        """Test creating medclass"""
        medclass = MedClass.objects.create(name="Analgésico")

        self.assertEqual(str(medclass), "Analgésico")

    def test_create_medicine_presentation(self):
        """Test creating medicine presentation instance in the DB."""
        medpres = MedicinePresentation.objects.create(name="Óvulo")

        self.assertEqual(str(medpres), medpres.name)

    def test_create_medicine(self):
        """Test creating a medicine object in the DB."""
        medicine = Medicine.objects.create(name="Aspirina")

        self.assertEqual(str(medicine),
                         f'Name: {medicine.name}, Batch: {medicine.batch}')

    def test_create_contact(self):
        """Test creating contact object in the DB."""
        contact = Contact.objects.create(name="Contact Name")

        self.assertEqual(str(contact), f'{contact.name} {contact.lastname}')

    def test_create_phone_number(self):
        """Test creating phone number for a contact instance."""
        contact = Contact.objects.create(name="Contact Name")
        phone_number = PhoneNumber.objects.create(
            contact=contact,
            number='+5359103546'
        )

        self.assertEqual(contact.name, phone_number.contact.name)

    def test_create_note(self):
        """Test creating a note object in the DB."""
        note = Note.objects.create(note="Test Note")

        self.assertEqual(str(note), f'Note No.: {note.id}.')

    def test_create_working_site(self):
        """Test creating working site instance in the DB."""
        workingsite = WorkingSite.objects.create(name="Test Name")

        self.assertEqual(str(workingsite), workingsite.name)
