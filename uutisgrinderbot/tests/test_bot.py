import unittest
from datetime import datetime, timezone
from unittest.mock import patch
import bot


class Tests(unittest.TestCase):
    def test_winter_summer_delivery(self):
        for month, utc_hour in [(1, 7), (7, 6)]:
            self.assertTrue(bot.is_delivery_time(datetime(2026, month, 15, utc_hour, tzinfo=timezone.utc)))
            self.assertFalse(bot.is_delivery_time(datetime(2026, month, 15, utc_hour + 1, tzinfo=timezone.utc)))

    def test_dst_transition_dates(self):
        for day, good_hour in [("2026-03-29", 6), ("2026-10-25", 7)]:
            runs = [h for h in (6, 7) if bot.is_delivery_time(datetime.fromisoformat(f"{day}T{h:02}:00:00+00:00"))]
            self.assertEqual(runs, [good_hour])

    def test_previous_calendar_day_across_dst(self):
        for day, hours in [("2026-03-30", 23), ("2026-10-26", 25)]:
            start, end = bot.previous_day(datetime.fromisoformat(day + "T07:00:00+00:00"))
            self.assertEqual(start.hour, 0)
            self.assertEqual(end.hour, 0)
            duration = end.astimezone(timezone.utc) - start.astimezone(timezone.utc)
            self.assertEqual(duration.total_seconds(), hours * 3600)

    def test_year_boundary(self):
        start, end = bot.previous_day(datetime(2027, 1, 1, 7, tzinfo=timezone.utc))
        self.assertEqual(str(start.date()), "2026-12-31")
        self.assertEqual(str(end.date()), "2027-01-01")

    def test_chunks_preserve_unicode_and_content(self):
        text = ("Talous 📊: ääkköset\n" * 500) + "a" * 8000
        parts = bot.split_messages(text)
        self.assertEqual("".join(parts), text)
        self.assertTrue(all(len(p.encode("utf-16-le")) // 2 <= 3500 for p in parts))

    def test_citations_visible_and_deduplicated(self):
        part = {"type": "output_text", "text": "Uutinen CITE ja toinen CITE.", "annotations": [
            {"type": "url_citation", "url": "https://yle.fi/a/123", "start_index": 8, "end_index": 12},
            {"type": "url_citation", "url": "https://yle.fi/a/123", "start_index": 23, "end_index": 27},
        ]}
        # Locate the second marker rather than depend on a hand-counted index.
        part["annotations"][1].update(start_index=part["text"].rindex("CITE"), end_index=part["text"].rindex("CITE") + 4)
        response = {"status": "completed", "output": [{"type": "web_search_call"}, {"type": "message", "content": [part]}]}
        result = bot.cited_text(response)
        self.assertIn("Uutinen [1] ja toinen [1].", result)
        self.assertEqual(result.count("https://yle.fi/a/123"), 1)

    def test_missing_search_or_sources_fail_closed(self):
        for response in [
            {"status": "incomplete", "output": []},
            {"status": "completed", "output": []},
            {"status": "completed", "output": [{"type": "web_search_call"}]},
        ]:
            with self.assertRaises(bot.BotError):
                bot.cited_text(response)

    def test_error_does_not_expose_token(self):
        with patch("bot.urlopen", side_effect=bot.URLError("https://api.telegram.org/botSECRET/sendMessage")):
            with self.assertRaises(bot.BotError) as error:
                bot.post("https://example.org", {})
        self.assertNotIn("SECRET", str(error.exception))

    def test_only_expected_bot_and_private_chat(self):
        with patch("bot.telegram", return_value={"username": "OtherBot"}):
            with self.assertRaises(bot.BotError):
                bot.check_recipient("token", "123")
        with patch("bot.telegram", side_effect=[{"username": "Uutisgrinderbot"}, {"type": "group"}]):
            with self.assertRaises(bot.BotError):
                bot.check_recipient("token", "123")

    def test_schedule_skips_before_credentials_or_network(self):
        with patch("sys.argv", ["bot.py", "scheduled"]), patch("bot.is_delivery_time", return_value=False), patch("bot.post") as post:
            bot.main()
            post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
