import datetime

from qdb.models import Quote


def make_quote(body='', submitted_at=None, submitter_ip=None, approved=False):
	if not submitted_at:
		submitted_at = datetime.datetime.now()
	return Quote(body, submitted_at, submitter_ip, approved)


def test_submitted_at_print_is_correct_type(db):
	dt = datetime.datetime(2015, 1, 1, 12, 0, 0)
	quote = make_quote(submitted_at=dt)
	assert isinstance(quote.submitted_at_print, datetime.datetime)

	dt = datetime.datetime(2015, 1, 1, 0, 0, 0)
	quote = make_quote(submitted_at=dt)
	assert not isinstance(quote.submitted_at_print, datetime.datetime)
	assert isinstance(quote.submitted_at_print, datetime.date)
