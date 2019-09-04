from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from djangoldp.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import loader
from django.utils.timezone import now

class Faq (Model):
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="Catégorie de question")
    
    def __str__(self):
        return self.question
    
class Collective (Model):
    name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mail")
    website = models.CharField(max_length=50, blank=True, null=True, verbose_name="Site web")
    facebook = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lien Facebook")
    twitter = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lien Twitter")
    comingsoon = models.BooleanField(default=False, verbose_name="Coming Soon")
    img = models.ImageField(blank=True, null=True, verbose_name="Illustration du collectif")
    
    def __str__(self):
        return self.name
        
class Testimony (Model):
    name = models.CharField(max_length=50, verbose_name="Nom de l'indépendant")
    statut = models.CharField(max_length=50, verbose_name="Statut")
    porteur = models.BooleanField(choices =((True, 'Porteur'), (False, "Membre")) ,default=True, verbose_name="Porteur de cellule")
    img = models.ImageField(blank=True, null=True, verbose_name="Photo")
    text = models.TextField(blank=True, null=True, verbose_name="Témoignage")
    
    def __str__(self):
        return self.name

class Regionevent (Model):
    name = models.CharField(max_length=50, verbose_name="Région")
    
    def __str__(self):
        return self.name
        
class Typeevent (Model):
    name = models.CharField(max_length=20, verbose_name="Type d'évènement")
    
    def __str__(self):
        return self.name

class Locationevent (Model):
    name = models.CharField(max_length=50, verbose_name="Lieu, établissement")
    address = models.TextField(max_length=225, blank=True, null=True, verbose_name="Adresse")
    
    def __str__(self):
        return self.name


class Event (Model):
    name = models.CharField(max_length=50, verbose_name="Nom de l'évènement")
    region = models.ForeignKey(Regionevent, verbose_name="Région")
    type = models.ForeignKey(Typeevent, verbose_name="Type d'évènement")
    startdate =  models.DateTimeField(verbose_name="Date et heure de début")
    enddate =  models.DateTimeField(verbose_name="Date et heure de fin")
    img = models.ImageField(blank=True, null=True, verbose_name="Illustration de l'évènement")
    location = models.ForeignKey(Locationevent, blank=True, null=True, verbose_name="Lieu de l'évènement")
    description = models.TextField(verbose_name="Description")
    link = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lien internet")
    facebook = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lien Facebook")
    class Meta : 
        ordering = ["startdate"]
    
    def __str__(self):
        return self.name

class Client (Model):
    name = models.CharField(max_length=50, verbose_name="Nom du client")
    link =  models.CharField(max_length=50, blank=True, null=True, verbose_name="Site internet")
    img = models.ImageField(blank=True, null=True, verbose_name="Logo")
    
    def __str__(self):
        return self.name
        
class Howareyou (Model):
    name = models.CharField(max_length=50, verbose_name="Comment vas-tu ?")

    def __str__(self):
        return self.name

class Howhelp (Model):
    name = models.CharField(max_length=50, verbose_name="Comment peut-on t'aider ?")
    keyword = models.CharField(max_length=15, verbose_name="mot-clé", default="client")
    
    def __str__(self):
        return self.name

class Workwish (Model):
    name = models.CharField(max_length=50, verbose_name="Souhait de type de travail du client")
    
    def __str__(self):
        return self.name

CONTACT_STATUSES = (('to be dispatched', "À dispatcher à l’extérieur"), ('dispatched', "Dispatché à l’extérieur"), ('to be validated', "Devis en attente de validation"), ('refused', "Devis refusé"), ('validated', "Devis validé"), ('invoice sent', "Facturé"), ('paid', "Encaissé par la cellule"))


class Contact (Model) :
    name = models.CharField(max_length=250)
    howareyou = models.ForeignKey(Howareyou)
    howhelp = models.ForeignKey(Howhelp)
    domaine = models.CharField(blank=True, null=True, max_length=250)
    clientlocation = models.CharField(blank=True, null=True, max_length=250)
    workwish = models.ForeignKey(Workwish, blank=True, null=True)
    project = models.CharField(blank=True, null=True, max_length=250)
    document = models.CharField(blank=True, null=True, max_length=250)
    budget = models.CharField(blank=True, null=True, max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(blank=True, null=True, max_length=20)
    textfreelance = models.CharField(blank=True, null=True, max_length=250)
    textporteur = models.CharField(blank=True, null=True, max_length=250)
    textautre = models.CharField(blank=True, null=True, max_length=250)
    date = models.DateTimeField(default=now, blank=True)
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    collective = models.ForeignKey(Collective, blank=True, null=True)
    status = models.CharField(max_length=20, choices=CONTACT_STATUSES, blank=True, null=True)
    
    class Meta:
        anonymous_perms = ['view', 'add']
    
    def __str__(self):
        return self.name

@receiver(post_save, sender=Contact)
def send_email_on_contact(sender, instance, created, **kwargs):
    if created:
       message = loader.render_to_string('contact_email.txt', {'contact': instance})
       send_mail('Une nouvelle demande de contact', message, 'capitaines@happy-dev.fr', ['capitaines@happy-dev.fr'])
