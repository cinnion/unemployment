"""
The model for our job applications and job postings (for LLM training and future reference).
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _


class JobPost(models.Model):
    """
    A database record for storing job posts for LLM training.
    """

    class Meta:
        """
        Override our table name.
        """
        db_table = "job_posts"
        db_table_comment = "Tracks the actual job postings for teaching an LLM to scrape for us."

    id = models.BigAutoField(
        _("id"),
        primary_key=True,
        help_text=_(
            "The primary key for the job post"
        ),
        db_comment="Primary key",
    )
    raw_url = models.URLField(
        _("raw job posting url"),
        max_length=2048,
        blank=False,
        null=False,
        unique=True,
        help_text=_(
            "The raw URL from the address bar for a job posting, with all the tracking and other cruft included."
        ),
        db_comment="The raw URL of the job posting.",
    )
    clean_url = models.URLField(
        _("clean job posting url"),
        max_length=2048,
        blank=True,
        null=True,
        help_text=_(
            "The cleaned up URL for the job posting, if applicable. Use notes for other job sources"
        ),
        db_comment="The cleaned up URL of job posting, if available.",
    )
    http_status = models.IntegerField(
        _("the HTTP status returned when requesting the job posting."),
        help_text=_(
            "The HTTP status returned when requesting the job posting."
        ),
        db_comment="The HTTP status returned when requesting the job posting.",
    )
    status_text = models.CharField(
        _("the status text returned when requesting the job posting."),
        max_length=256,
        blank=False,
        null=False,
        help_text=_(
            "The status text returned when requesting the job posting."
        ),
        db_comment="The status text returned when requesting the job posting.",
    )
    contents = models.TextField(
        _("job post contents"),
        blank=False,
        null=False,
        help_text=_(
            "The raw page contents for the job post."
        ),
        db_comment="The raw page contents for the job post.",
    )
    description = models.TextField(
        _("job post description"),
        blank=True,
        null=True,
        help_text=_(
            "The description according to the job post."
        ),
        db_comment="The description according to the job post."
    )
    company = models.CharField(
        _("company name"),
        max_length=64,
        help_text=_(
            "The name of the company."
        ),
        db_comment="Name of company."
    )
    title = models.CharField(
        _("job title"),
        max_length=128,
        help_text=_(
            "The job title."
        ),
        db_comment="Job title."
    )
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
        null=True,
        help_text=_(
            "When the record was created"
        ),
        db_comment="Record created at.",
    )
    updated_at = models.DateTimeField(
        _("updated_at"),
        auto_now=True,
        help_text=_(
            "When the record was last updated",
        ),
        db_comment="Record last updated at."
    )


class JobApplication(models.Model):
    """
    A database record for storing information about job applications.
    """

    class Meta:
        """
        Override our table name.
        """
        db_table = "job_applications"
        db_table_comment = "Tracks a job application made by a user."

    id = models.BigAutoField(
        _("id"),
        primary_key=True,
        help_text=_(
            "The primary key for the job application"
        ),
        db_comment="Primary key",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user id"),
        related_name="job_applications",
        db_comment="The user who submitted the application."
    )
    when = models.DateField(
        _("when"),
        default=localtime,
        blank=True,
        help_text=_(
            "The date when the application was submitted"
        ),
        db_comment="Date of application."
    )
    company = models.CharField(
        _("company name"),
        max_length=64,
        help_text=_(
            "The name of the company."
        ),
        db_comment="Name of company."
    )
    title = models.CharField(
        _("job title"),
        max_length=128,
        help_text=_(
            "The job title."
        ),
        db_comment="Job title."
    )
    posting = models.URLField(
        _("job posting url"),
        max_length=2048,
        blank=True,
        null=True,
        help_text=_(
            "The URL for the job posting, if applicable. Use notes for other job sources"
        ),
        db_comment="URL of job posting, if applicable."
    )
    saved_posting = models.ForeignKey(
        JobPost,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("saved job post id"),
        related_name="job_post",
        db_comment="The saved job posting."
    )
    confirm = models.URLField(
        _("confirmation email url"),
        blank=True,
        null=True,
        help_text=_(
            "The URL of the confirmation email"
        ),
        db_comment="URL for application confirmation, if applicable."
    )
    notes = models.TextField(
        _("notes"),
        max_length=4096,
        blank=True,
        null=True,
        help_text=_(
            "Notes about this job, such as alternate sources, expected salary, etc."
        ),
        db_comment="Notes"
    )
    active = models.BooleanField(
        _("application still active"),
        default=True,
        help_text=_(
            "True if the job application is still potentially active"
        ),
        db_comment="Application is still outstanding."
    )
    interviews = models.PositiveSmallIntegerField(
        _("interviews"),
        default=0,
        help_text=_(
            "The number of interviews. More details like dates can go in the notes field."
        ),
        db_comment="The number of interviews for the job."
    )
    rejected = models.DateField(
        _("rejection date"),
        blank=True,
        null=True,
        help_text=(
            "When a job rejection letter was received"
        ),
        db_comment="Date of rejection notice."
    )
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
        null=True,
        help_text=_(
            "When the record was created"
        ),
        db_comment="Record created at.",
    )
    updated_at = models.DateTimeField(
        _("updated_at"),
        auto_now=True,
        help_text=_(
            "When the record was last updated",
        ),
        db_comment="Record last updated at."
    )

    @property
    def interviewed(self) -> bool:
        """
        Whether we have interviewed for the job.
        """
        if self.interviews > 0:
            return True

        return False

    def __str__(self):
        """
        Method used when converting to a string. Only return a far simpler representation
        of the record in this instance.
        """
        return f"{self.when}: {self.title} @ {self.company}"
