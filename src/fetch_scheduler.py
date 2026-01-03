import argparse
import time
from datetime import datetime
from src.data_fetcher_api import fetch_and_store_coins


def run_scheduler(coins, interval_minutes=60, days=365, dest_dir='data/processed', parquet=False):
    print(f"Starting fetch scheduler: coins={coins}, interval_minutes={interval_minutes}")
    try:
        while True:
            print(f"[{datetime.utcnow()}] Fetching data...")
            res = fetch_and_store_coins(coins, days=days, dest_dir=dest_dir, parquet=parquet)
            print(res)
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        print('Scheduler stopped')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--coins', nargs='+', default=['bitcoin','ethereum'], help='List of coin ids to fetch')
    parser.add_argument('--interval', type=int, default=60, help='Interval in minutes between fetches')
    parser.add_argument('--days', type=int, default=365, help='Days history to fetch')
    parser.add_argument('--parquet', action='store_true', help='Store as parquet instead of csv')
    parser.add_argument('--dest', default='data/processed', help='Destination directory')

    args = parser.parse_args()
    run_scheduler(args.coins, interval_minutes=args.interval, days=args.days, dest_dir=args.dest, parquet=args.parquet)