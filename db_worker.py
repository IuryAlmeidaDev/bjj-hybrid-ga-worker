# ga-worker/db_worker.py
import os
import json
from dataclasses import asdict
from optimizer import evolve_microcycle


DEFAULT_EXERCISES = {
    "A": [
        "supino_inclinado",
        "supino_reto",
        "desenvolvimento_halteres",
        "elevacao_lateral",
        "triceps_corda",
        "manguito_rotador",
    ],
    "B": [
        "barra_fixa",
        "remada_curvada",
        "remada_unilateral",
        "face_pull",
        "rosca_martelo",
        "farmers_walk",
    ],
    "C": [
        "agachamento_livre",
        "rdl_terra_romeno",
        "agachamento_bulgaro",
        "elevacao_pelvica",
        "cadeira_flexora",
        "prancha_abdominal",
        "panturrilha_em_pe",
    ],
}


def run_optimization_cycle(database_url: str | None = None) -> dict:
    avg_rpe = 7.5
    stressed_tags: list[str] = []

    if database_url:
        try:
            import psycopg

            with psycopg.connect(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COALESCE(AVG(rpe_intensity), 6.5)
                        FROM bjj_sessions
                        WHERE session_date >= CURRENT_DATE - INTERVAL '28 days'
                        """
                    )
                    row = cur.fetchone()
                    if row and row[0] is not None:
                        avg_rpe = float(row[0])

                    cur.execute(
                        """
                        SELECT DISTINCT UNNEST(body_stress_tags)
                        FROM bjj_sessions
                        WHERE session_date >= CURRENT_DATE - INTERVAL '14 days'
                        """
                    )
                    stressed_tags = [r[0] for r in cur.fetchall() if r[0]]
        except Exception as exc:
            print(f"[ga-worker] Using local context fallback ({exc})")

    microcycle_plan = {}
    total_fitness = 0.0

    for code, slugs in DEFAULT_EXERCISES.items():
        ctx = {
            "avg_bjj_rpe": avg_rpe,
            "stressed_tags": stressed_tags,
            "exercises": slugs,
        }
        best_genes, score = evolve_microcycle(ctx, generations=50, pop_size=30, seed=42)
        microcycle_plan[code] = [asdict(g) for g in best_genes]
        total_fitness += score

    result_payload = {
        "avg_bjj_rpe_4w": round(avg_rpe, 2),
        "stressed_tags": stressed_tags,
        "total_fitness_score": round(total_fitness, 2),
        "workouts": microcycle_plan,
    }

    if database_url:
        try:
            import psycopg

            with psycopg.connect(database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO optimized_plans (user_id, generation_number, fitness_score, plan_payload)
                        VALUES ('00000000-0000-0000-0000-000000000001', 50, %s, %s::jsonb)
                        """,
                        (result_payload["total_fitness_score"], json.dumps(result_payload)),
                    )
                conn.commit()
        except Exception as exc:
            print(f"[ga-worker] Skipped DB write ({exc})")

    return result_payload


if __name__ == "__main__":
    db_url = os.environ.get("DATABASE_URL")
    output = run_optimization_cycle(db_url)
    print(json.dumps(output, indent=2, ensure_ascii=False))
