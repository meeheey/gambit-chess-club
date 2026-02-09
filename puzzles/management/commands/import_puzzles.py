import csv
import os
from django.core.management.base import BaseCommand
from puzzles.models import Puzzle
from django.db import transaction

class Command(BaseCommand):
    help = 'Import puzzles from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of records to import')
        parser.add_argument('--skip-existing', action='store_true', help='Skip existing puzzles')
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        limit = options['limit']
        skip_existing = options['skip_existing']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f"File {csv_file} not found"))
            return
        
        puzzles_created = 0
        puzzles_skipped = 0
        puzzles_updated = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            total_rows = 0
            
            for i, row in enumerate(reader):
                total_rows += 1
                if limit and i >= limit:
                    break
                
                # Filter for Kings Gambit
                opening_tags = row.get('OpeningTags', '')
                if not opening_tags or 'Kings_Gambit' not in opening_tags:
                    continue
                
                try:
                    # Parse numeric fields with error handling
                    rating = self.parse_int(row.get('Rating', '0'))
                    rating_deviation = self.parse_int(row.get('RatingDeviation', '0'))
                    popularity = self.parse_int(row.get('Popularity', '0'))
                    nb_plays = self.parse_int(row.get('NbPlays', '0'))
                    
                    # Check if puzzle already exists
                    existing_puzzle = Puzzle.objects.filter(puzzle_id=row['PuzzleId']).first()
                    
                    if existing_puzzle:
                        if skip_existing:
                            puzzles_skipped += 1
                            continue
                        
                        # Update existing puzzle
                        existing_puzzle.fen = row['FEN']
                        existing_puzzle.moves = row['Moves']
                        existing_puzzle.rating = rating
                        existing_puzzle.rating_deviation = rating_deviation
                        existing_puzzle.popularity = popularity
                        existing_puzzle.nb_plays = nb_plays
                        existing_puzzle.themes = row.get('Themes', '')
                        existing_puzzle.game_url = row.get('GameUrl', '')
                        existing_puzzle.opening_tags = opening_tags
                        existing_puzzle.save()
                        puzzles_updated += 1
                    else:
                        # Create new puzzle
                        Puzzle.objects.create(
                            puzzle_id=row['PuzzleId'],
                            fen=row['FEN'],
                            moves=row['Moves'],
                            rating=rating,
                            rating_deviation=rating_deviation,
                            popularity=popularity,
                            nb_plays=nb_plays,
                            themes=row.get('Themes', ''),
                            game_url=row.get('GameUrl', ''),
                            opening_tags=opening_tags,
                        )
                        puzzles_created += 1
                    
                    if (puzzles_created + puzzles_updated) % 100 == 0:
                        self.stdout.write(f"Processed {i+1} rows... Created: {puzzles_created}, Updated: {puzzles_updated}")
                        
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"Error processing row {i+1} (PuzzleId: {row.get('PuzzleId', 'unknown')}): {e}"
                    ))
                    continue
        
        self.stdout.write(self.style.SUCCESS(
            f"Import complete! Processed {total_rows} rows from CSV."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Results: Created {puzzles_created}, Updated {puzzles_updated}, Skipped {puzzles_skipped} puzzles"
        ))
    
    def parse_int(self, value):
        """Parse integer from string, handling floats and empty strings"""
        if not value:
            return 0
        try:
            # Handle float values like "1107.5"
            return int(float(value))
        except (ValueError, TypeError):
            return 0