"""
Test for the models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

UserProfile = get_user_model()


class ModelTests(TestCase):
    """Test models."""

    def test_user_profile(self):
        """Test creating user profile in the API."""
        email = 'userprofile@example.com'
        id = 1
        user = UserProfile.objects.create_user(
            id=id,
            email=email,
            password='testpass123',
            name='Test Name',
        )

        self.assertEqual(str(user), email)

    def test_create_medclass(self):
        """Test creating medclass"""
        medclass = models.MedClass.objects.create(name="Analgésico")

        self.assertEqual(str(medclass), "Analgésico")

    def test_create_medicine_presentation(self):
        """Test creating medicine presentation instance in the DB."""
        medpres = models.MedicinePresentation.objects.create(name="Óvulo")

        self.assertEqual(str(medpres), medpres.name)

    def test_create_medicine(self):
        """Test creating a medicine object in the DB."""
        medicine = models.Medicine.objects.create(name="Aspirina")

        self.assertEqual(str(medicine),
                         f'Name: {medicine.name}, Quantity: {medicine.quantity}'
                         )

    def test_create_contact(self):
        """Test creating contact object in the DB."""
        contact = models.Contact.objects.create(name="Contact Name")

        self.assertEqual(str(contact), f'{contact.name} {contact.lastname}')

    def test_create_phone_number(self):
        """Test creating phone number for a contact instance."""
        contact = models.Contact.objects.create(name="Contact Name")
        phone_number = models.PhoneNumber.objects.create(
            contact=contact,
            number='+5359103546'
        )

        self.assertEqual(contact.name, phone_number.contact.name)

    def test_create_note(self):
        """Test creating a note object in the DB."""
        note = models.Note.objects.create(note="Test Note")

        self.assertEqual(str(note), f'Note No.: {note.id}.')

    def test_create_working_site(self):
        """Test creating working site instance in the DB."""
        workingsite = models.WorkingSite.objects.create(name="Test Name")

        self.assertEqual(str(workingsite), workingsite.name)

    def test_create_medic(self):
        """Test creating a medic contact instance."""
        contact = models.Contact.objects.create(name="Contact for Medic")

        medic = models.Medic.objects.create(contact=contact,
                                            specialty="Geriatra")

        self.assertEqual(str(medic), f'{contact.name}: {medic.specialty}')

    def test_create_donor(self):
        """Test creating a donor contact instance."""
        contact = models.Contact.objects.create(name="Contact for Donor")

        donor = models.Donor.objects.create(contact=contact, city="Florida")

        self.assertEqual(str(donor), f'{contact.name}: {donor.city}')

    def test_create_municipality(self):
        """Test creating munincipaliy."""
        mun = models.Municipality.objects.create(name="Gibara", province="HOL")

        self.assertEqual(str(mun), f'{mun.name}, {mun.province}')

    def test_create_denomination(self):
        """Test creating a denomination instance."""
        denom = models.Denomination.objects.create(name="Metodista")

        self.assertEqual(str(denom), f'{denom.name}')

    def test_create_church(self):
        """Test creating a church."""
        denomination = models.Denomination.objects.create(name="Metodista")
        priest = models.Contact.objects.create(name='Pastor')
        church = models.Church.objects.create(name="Iglesia",
                                              denomination=denomination,
                                              priest=priest)

        self.assertEqual(str(church), f'{church.name}, {church.denomination}')

    def test_create_disease(self):
        """Test creating new desease instance."""
        disease = models.Disease.objects.create(name="Hipotiroidismo")

        self.assertEqual(str(disease), disease.name)

    def test_create_donee(self):
        """Test creating a donee in the system."""
        denomination = models.Denomination.objects.create(name="Metodista")
        priest = models.Contact.objects.create(name='Pastor')
        church = models.Church.objects.create(name="Iglesia",
                                              denomination=denomination,
                                              priest=priest)
        contact = models.Contact.objects.create(name="Contact for Donee")

        donee = models.Donee.objects.create(
            contact=contact,
            ci="12345678987",
            church=church,
        )

        self.assertEqual(str(donee), f'Donee: {donee.code}')

    def test_create_treatment(self):
        """Test create treatment for a donee."""
        denomination = models.Denomination.objects.create(name="Metodista")
        priest = models.Contact.objects.create(name='Pastor')
        church = models.Church.objects.create(name="Iglesia",
                                              denomination=denomination,
                                              priest=priest)
        contact = models.Contact.objects.create(name="Contact for Donee")
        donee = models.Donee.objects.create(
            contact=contact,
            ci="12345678987",
            church=church,
        )
        disease = models.Disease.objects.create(name="Disease for treatment")

        treatment = models.Treatment.objects.create(
            donee=donee,
            disease=disease,
        )

        self.assertEqual(str(treatment), f'{str(donee)}, {disease.name}')
