from django.db import models
import markdown

class Message(models.Model):

	publish_start = models.DateField('Start publish date', blank=True, null=True)
	publish_end   = models.DateField('End publish date', blank=True, null=True)

	subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
	order   = models.IntegerField('Order', blank=True, null=True)
	name 	= models.CharField("Title", max_length=200)
	image   = models.ImageField('Image', upload_to="uploads/message/", max_length=300, blank=True)
	date    = models.DateTimeField('Date', blank=True, null=True)
	text 	= models.TextField('Text', null=True, blank=True)

	is_event = models.BooleanField('Is an event', default=True)
	location = models.CharField('Location', max_length=200, blank=True, null=True)
	start 	 = models.DateTimeField('Start', blank=True, null=True)
	end 	 = models.DateTimeField('End', blank=True, null=True)

	mailing_lists = models.ManyToManyField('MailingList')

	def __str__(self):
		return self.name


	def to_html(self):
		if self.text is None: return ''
		return markdown.markdown(self.text)