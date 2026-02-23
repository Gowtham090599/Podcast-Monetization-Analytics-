from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from faker import Faker

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out_dir", type=str, default="data")
    p.add_argument("--n_creators", type=int, default=75000)
    p.add_argument("--days", type=int, default=180)
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    fake = Faker()
    Faker.seed(args.seed)

    # --- dimensions ---
    categories = ["News", "Education", "Comedy", "Sports", "True Crime", "Business", "Health", "Technology"]
    creator_tiers = ["Small", "Mid", "Large"]

    creators = []
    for cid in range(1, args.n_creators + 1):
        created_at = pd.Timestamp.today().normalize() - pd.Timedelta(days=int(rng.integers(30, 720)))
        tier = rng.choice(creator_tiers, p=[0.65, 0.28, 0.07])
        country = rng.choice(["US", "CA", "GB", "AU", "DE"], p=[0.62, 0.10, 0.12, 0.08, 0.08])
        creators.append({
            "creator_id": cid,
            "created_at": created_at,
            "tier": tier,
            "country": country,
        })
    creators_df = pd.DataFrame(creators)

    podcasts = []
    n_podcasts = int(args.n_creators * 1.15)
    for pid in range(1, n_podcasts + 1):
        creator_id = int(rng.integers(1, args.n_creators + 1))
        category = rng.choice(categories)
        podcasts.append({
            "podcast_id": pid,
            "creator_id": creator_id,
            "category": category,
            "created_at": creators_df.loc[creators_df.creator_id == creator_id, "created_at"].iloc[0] + pd.Timedelta(days=int(rng.integers(0, 30)))
        })
    podcasts_df = pd.DataFrame(podcasts)

    # --- events / lifecycle ---
    # stages: signup -> eligible -> enroll -> first_payout
    base_date = pd.Timestamp.today().normalize() - pd.Timedelta(days=args.days)
    dates = pd.date_range(base_date, periods=args.days, freq="D")

    # Experiment flag: "new_enrollment_banner" (A/B)
    creators_df["experiment_group"] = rng.choice(["control", "treatment"], size=len(creators_df), p=[0.5, 0.5])

    # eligibility depends on tier + age
    age_days = (pd.Timestamp.today().normalize() - creators_df["created_at"]).dt.days
    tier_factor = creators_df["tier"].map({"Small": 0.20, "Mid": 0.35, "Large": 0.55}).values
    eligible_prob = np.clip(0.15 + tier_factor + (age_days.values / 2000), 0, 0.95)
    creators_df["eligible"] = rng.binomial(1, eligible_prob)

    # enrollment probability: eligible + experiment treatment uplift
    uplift = np.where(creators_df["experiment_group"].values == "treatment", 0.06, 0.0)
    enroll_prob = np.clip(0.08 + 0.35*creators_df["eligible"].values + uplift + 0.08*(creators_df["tier"].values=="Large"), 0, 0.92)
    creators_df["enrolled"] = rng.binomial(1, enroll_prob)

    # payouts probability: enrolled + tier + category mix (proxy)
    payout_prob = np.clip(0.05 + 0.55*creators_df["enrolled"].values + 0.10*(creators_df["tier"].values=="Large"), 0, 0.90)
    creators_df["first_payout"] = rng.binomial(1, payout_prob)

    # Create event log
    events = []
    for row in creators_df.itertuples(index=False):
        # signup event at created_at
        events.append({"event_ts": row.created_at, "creator_id": row.creator_id, "event_name": "signup"})
        # eligible event sometime later if eligible
        if row.eligible == 1:
            events.append({"event_ts": row.created_at + pd.Timedelta(days=int(rng.integers(5, 60))), "creator_id": row.creator_id, "event_name": "eligible"})
        if row.enrolled == 1:
            events.append({"event_ts": row.created_at + pd.Timedelta(days=int(rng.integers(10, 90))), "creator_id": row.creator_id, "event_name": "enroll"})
        if row.first_payout == 1:
            events.append({"event_ts": row.created_at + pd.Timedelta(days=int(rng.integers(20, 120))), "creator_id": row.creator_id, "event_name": "first_payout"})
    events_df = pd.DataFrame(events)

    # --- episodes + listening ---
    # episodes per podcast per day depends on tier
    tier_rate = {"Small": 0.03, "Mid": 0.06, "Large": 0.10}  # expected episodes/day
    episodes = []
    listens = []
    ep_id = 1
    for d in dates:
        # sample active podcasts today
        # publish probability by creator tier
        todays = podcasts_df.sample(n=min(6000, len(podcasts_df)), random_state=int(d.strftime("%j")))
        for r in todays.itertuples(index=False):
            tier = creators_df.loc[creators_df.creator_id == r.creator_id, "tier"].iloc[0]
            p_publish = tier_rate[tier]
            if rng.random() < p_publish:
                episodes.append({
                    "episode_id": ep_id,
                    "podcast_id": r.podcast_id,
                    "creator_id": r.creator_id,
                    "published_at": d,
                    "duration_min": int(np.clip(rng.normal(38, 14), 8, 140))
                })
                # listens proxy: depends on tier + category
                base = {"Small": 250, "Mid": 800, "Large": 3000}[tier]
                cat_boost = 1.0 + 0.08*(r.category in ["True Crime", "Comedy"]) + 0.05*(r.category in ["News","Business"])
                l = int(np.clip(rng.lognormal(mean=np.log(base*cat_boost), sigma=0.45), 20, 250000))
                listens.append({
                    "event_date": d,
                    "episode_id": ep_id,
                    "podcast_id": r.podcast_id,
                    "creator_id": r.creator_id,
                    "listens": l
                })
                ep_id += 1

    episodes_df = pd.DataFrame(episodes)
    listens_df = pd.DataFrame(listens)

    # --- revenue (creator daily) ---
    # Revenue depends on listens + enrolled
    if not listens_df.empty:
        rev = listens_df.merge(creators_df[["creator_id","enrolled"]], on="creator_id", how="left")
        # enrolled creators get higher RPM
        rpm = np.where(rev["enrolled"].values==1, rng.normal(18, 3, len(rev)), rng.normal(6, 2, len(rev)))
        revenue = np.maximum(0, (rev["listens"].values/1000) * rpm)
        rev_df = pd.DataFrame({
            "event_date": rev["event_date"].values,
            "creator_id": rev["creator_id"].values,
            "podcast_id": rev["podcast_id"].values,
            "episode_id": rev["episode_id"].values,
            "revenue_usd": np.round(revenue, 2)
        })
    else:
        rev_df = pd.DataFrame(columns=["event_date","creator_id","podcast_id","episode_id","revenue_usd"])

    # --- write outputs ---
    creators_df.to_csv(out_dir / "creators.csv", index=False)
    podcasts_df.to_csv(out_dir / "podcasts.csv", index=False)
    episodes_df.to_csv(out_dir / "episodes.csv", index=False)
    events_df.to_csv(out_dir / "creator_events.csv", index=False)
    listens_df.to_csv(out_dir / "listening_events.csv", index=False)
    rev_df.to_csv(out_dir / "revenue_events.csv", index=False)

    print(f"Wrote datasets to: {out_dir.resolve()}")
    print(f"creators: {len(creators_df):,} | podcasts: {len(podcasts_df):,} | episodes: {len(episodes_df):,} | events: {len(events_df):,} | listens: {len(listens_df):,} | revenue rows: {len(rev_df):,}")

if __name__ == "__main__":
    main()
