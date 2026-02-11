import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from web_page.models import ClubMember

API_URL = "https://fide-api.vercel.app/player_info/"


class Command(BaseCommand):
    help = "Update FIDE classical ratings and track rating changes"

    def handle(self, *args, **kwargs):

        members = ClubMember.objects.filter(
            is_active=True
        ).exclude(fide_id__isnull=True).exclude(fide_id="")

        self.stdout.write(f"\nUpdating {members.count()} members...\n")

        for member in members:
            try:
                response = requests.get(
                    API_URL,
                    params={
                        "fide_id": member.fide_id,
                        "history": "false"
                    },
                    timeout=10
                )

                if response.status_code != 200:
                    self.stdout.write(
                        self.style.WARNING(
                            f"HTTP {response.status_code} → {member.full_name}"
                        )
                    )
                    continue

                data = response.json()
                new_rating = data.get("classical_rating")

                if not new_rating:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No rating returned → {member.full_name}"
                        )
                    )
                    continue

                # Convert to int safely
                new_rating = int(new_rating)

                # If first time setting rating
                if member.rating is None:
                    member.rating = new_rating
                    member.previous_rating = None
                    member.rating_change = None
                    member.rating_updated_at = timezone.now()
                    member.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{member.full_name}: set to {new_rating}"
                        )
                    )
                    continue

                # If rating changed
                if member.rating != new_rating:
                    old_rating = member.rating
                    change = new_rating - old_rating

                    member.previous_rating = old_rating
                    member.rating = new_rating
                    member.rating_change = change
                    member.rating_updated_at = timezone.now()
                    member.save()

                    sign = "+" if change > 0 else ""
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{member.full_name}: {old_rating} → {new_rating} ({sign}{change})"
                        )
                    )
                else:
                    self.stdout.write(
                        f"{member.full_name}: unchanged ({member.rating})"
                    )

            except requests.exceptions.Timeout:
                self.stdout.write(
                    self.style.ERROR(f"Timeout → {member.full_name}")
                )

            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f"Request error → {member.full_name}: {str(e)}")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Unexpected error → {member.full_name}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("\nRating update finished.\n"))
