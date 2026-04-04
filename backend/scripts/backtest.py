"""
Backtesting script: Run 50 real marketing campaigns through PhantomCrowd
and compare simulated viral scores against known real-world outcomes.

Usage:
  cd backend
  source .venv/bin/activate
  python scripts/backtest.py [--agents 10] [--parallel 2]
"""

import asyncio
import json
import sys
import time
import os
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(str(Path(__file__).parent.parent))

from data.backtesting_campaigns import CAMPAIGNS
from app.core.config import settings
from app.services.persona_generator import generate_personas
from app.services.simulation_engine import _generate_single_reaction, _get_client, _analyze_results
from app.services.json_utils import extract_json


async def run_single_backtest(
    campaign: dict,
    num_agents: int = 10,
    index: int = 0,
    use_cd: bool = True,
) -> dict:
    """Run a single campaign through the Quick Test pipeline."""
    start = time.time()
    name = campaign["name"]
    content = campaign["content"]
    language = campaign["language"]

    try:
        # 1. Generate personas
        personas = await generate_personas(
            content=content,
            content_type="ad_copy",
            count=num_agents,
        )

        # 2. Run reactions in parallel
        client = _get_client()
        tasks = [
            _generate_single_reaction(client, p, content, "ad_copy", language)
            for p in personas
        ]
        reactions = []
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                reactions.append(result)
            except Exception:
                pass

        if not reactions:
            raise ValueError("No reactions generated")

        # 3. Compute stats
        sentiments = [r.get("sentiment", "neutral") for r in reactions]
        engagements = [r.get("engagement", "ignore") for r in reactions]
        scores = [r.get("sentiment_score", 0) for r in reactions]
        avg_score = sum(scores) / len(scores) if scores else 0

        sentiment_dist = {}
        for s in sentiments:
            sentiment_dist[s] = sentiment_dist.get(s, 0) + 1

        engagement_dist = {}
        for e in engagements:
            engagement_dist[e] = engagement_dist.get(e, 0) + 1

        # 4. Analyze results (get viral score)
        analysis = await _analyze_results(
            client=client,
            content=content,
            reactions=reactions,
            language=language,
        )

        raw_score = analysis.get("viral_score", 50)

        # 5. No CD in backtest (too slow with 27b model)
        penalty = 0
        final_score = raw_score
        controversy = {"has_controversy": False, "overall_risk": "skipped"}

        elapsed = time.time() - start

        result = {
            "index": index,
            "name": name,
            "expected_score": campaign["expected_score"],
            "raw_score": raw_score,
            "cd_penalty": penalty,
            "final_score": final_score,
            "avg_sentiment": round(avg_score, 2),
            "sentiment_dist": sentiment_dist,
            "engagement_dist": engagement_dist,
            "controversy_detected": controversy.get("has_controversy", False),
            "controversy_risk": controversy.get("overall_risk", "none"),
            "outcome": campaign["outcome"],
            "time_seconds": round(elapsed, 1),
            "error": None,
        }

        diff = final_score - campaign["expected_score"]
        marker = "✓" if abs(diff) <= 20 else "✗"
        print(
            f"  [{index+1:2d}/50] {marker} {name:45s} "
            f"Expected: {campaign['expected_score']:3d}  Got: {final_score:3d} "
            f"(raw:{raw_score} cd:-{penalty})  "
            f"Δ{diff:+d}  [{elapsed:.1f}s]"
        )
        return result

    except Exception as e:
        elapsed = time.time() - start
        print(f"  [{index+1:2d}/50] ✗ {name:45s} ERROR: {str(e)[:60]}  [{elapsed:.1f}s]")
        return {
            "index": index,
            "name": name,
            "expected_score": campaign["expected_score"],
            "raw_score": None,
            "cd_penalty": 0,
            "final_score": None,
            "outcome": campaign["outcome"],
            "time_seconds": round(elapsed, 1),
            "error": str(e)[:200],
        }


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=10, help="Agents per campaign")
    parser.add_argument("--parallel", type=int, default=2, help="Campaigns in parallel")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--count", type=int, default=50, help="Number of campaigns")
    parser.add_argument("--no-cd", action="store_true", help="Skip Controversy Detector (faster)")
    args = parser.parse_args()

    campaigns = CAMPAIGNS[args.start:args.start + args.count]

    print(f"PhantomCrowd Backtesting")
    print(f"========================")
    print(f"Model: {settings.llm_model}")
    print(f"CD Model: {settings.controversy_model}")
    print(f"Agents per campaign: {args.agents}")
    print(f"Parallel campaigns: {args.parallel}")
    print(f"Campaigns: {len(campaigns)}")
    print(f"Controversy Detector: {'ON' if not args.no_cd else 'OFF (--no-cd)'}")
    print()

    total_start = time.time()
    results = []

    # Run in batches of `parallel`
    sem = asyncio.Semaphore(args.parallel)

    async def run_with_sem(campaign, idx):
        async with sem:
            return await run_single_backtest(campaign, args.agents, idx)

    tasks = [run_with_sem(c, i + args.start) for i, c in enumerate(campaigns)]
    results = await asyncio.gather(*tasks)

    total_time = time.time() - total_start

    # Summary
    print(f"\n{'='*80}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*80}")

    valid = [r for r in results if r.get("final_score") is not None]
    errors = [r for r in results if r.get("error")]

    if not valid:
        print("No valid results!")
        return

    # Correlation calculation
    expected = [r["expected_score"] for r in valid]
    actual = [r["final_score"] for r in valid]

    n = len(valid)
    mean_e = sum(expected) / n
    mean_a = sum(actual) / n

    cov = sum((e - mean_e) * (a - mean_a) for e, a in zip(expected, actual)) / n
    std_e = (sum((e - mean_e) ** 2 for e in expected) / n) ** 0.5
    std_a = (sum((a - mean_a) ** 2 for a in actual) / n) ** 0.5

    correlation = cov / (std_e * std_a) if std_e * std_a > 0 else 0

    # Mean absolute error
    mae = sum(abs(e - a) for e, a in zip(expected, actual)) / n

    # Directional accuracy: does it correctly rank success > failure?
    correct_direction = 0
    total_pairs = 0
    for i, r1 in enumerate(valid):
        for r2 in valid[i+1:]:
            if r1["outcome"] != r2["outcome"]:
                total_pairs += 1
                if r1["outcome"] == "success" and r1["final_score"] > r2["final_score"]:
                    correct_direction += 1
                elif r1["outcome"] == "failure" and r1["final_score"] < r2["final_score"]:
                    correct_direction += 1

    dir_accuracy = correct_direction / total_pairs * 100 if total_pairs > 0 else 0

    # Within-bucket accuracy (score within ±1 bucket of expected)
    def get_bucket(score):
        if score <= 15: return 0
        if score <= 30: return 1
        if score <= 45: return 2
        if score <= 55: return 3
        if score <= 70: return 4
        if score <= 85: return 5
        return 6

    bucket_exact = sum(1 for e, a in zip(expected, actual) if get_bucket(e) == get_bucket(a))
    bucket_near = sum(1 for e, a in zip(expected, actual) if abs(get_bucket(e) - get_bucket(a)) <= 1)

    print(f"\nTotal campaigns:     {len(campaigns)}")
    print(f"Successful runs:     {len(valid)}")
    print(f"Errors:              {len(errors)}")
    print(f"Total time:          {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Avg time/campaign:   {total_time/len(campaigns):.1f}s")
    print()
    print(f"📊 ACCURACY METRICS:")
    print(f"  Pearson correlation:    {correlation:.3f}  {'✓ GOOD' if correlation >= 0.6 else '✗ NEEDS WORK' if correlation >= 0.4 else '✗ POOR'}")
    print(f"  Mean absolute error:    {mae:.1f} points")
    print(f"  Directional accuracy:   {dir_accuracy:.1f}%  (success > failure pairs)")
    print(f"  Exact bucket match:     {bucket_exact}/{n} ({bucket_exact/n*100:.0f}%)")
    print(f"  Near bucket (±1):       {bucket_near}/{n} ({bucket_near/n*100:.0f}%)")
    print()

    # Score distribution comparison
    print(f"📈 SCORE DISTRIBUTION:")
    print(f"  {'Bucket':<20s} {'Expected':>8s} {'Actual':>8s}")
    for lo, hi, label in [
        (0, 15, "Harmful (0-15)"),
        (16, 30, "Poor (16-30)"),
        (31, 45, "Below avg (31-45)"),
        (46, 55, "Average (46-55)"),
        (56, 70, "Good (56-70)"),
        (71, 85, "Very good (71-85)"),
        (86, 100, "Excellent (86+)"),
    ]:
        e_count = sum(1 for e in expected if lo <= e <= hi)
        a_count = sum(1 for a in actual if lo <= a <= hi)
        print(f"  {label:<20s} {e_count:>8d} {a_count:>8d}")

    print()

    # Worst misses
    diffs = [(r, r["final_score"] - r["expected_score"]) for r in valid]
    diffs.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"🎯 BIGGEST MISSES (top 10):")
    for r, diff in diffs[:10]:
        print(
            f"  {r['name']:45s} Expected:{r['expected_score']:3d} Got:{r['final_score']:3d} "
            f"Δ{diff:+d} {'(CD:' + r.get('controversy_risk','') + ')' if r.get('controversy_detected') else ''}"
        )

    # Save full results
    output_path = Path("data/backtest_results.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "meta": {
                "model": settings.llm_model,
                "cd_model": settings.controversy_model,
                "agents_per_campaign": args.agents,
                "total_campaigns": len(campaigns),
                "successful_runs": len(valid),
                "total_time_seconds": round(total_time, 1),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "metrics": {
                "pearson_correlation": round(correlation, 4),
                "mean_absolute_error": round(mae, 1),
                "directional_accuracy": round(dir_accuracy, 1),
                "exact_bucket_match": f"{bucket_exact}/{n}",
                "near_bucket_match": f"{bucket_near}/{n}",
            },
            "results": results,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Full results saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
