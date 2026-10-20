from optimizer import Gene, evaluate_fitness, evolve_microcycle


def test_evaluate_fitness_penalizes_stressed_joints():
    safe_plan = [
        Gene(slug="rdl_terra_romeno", sets=3, tier="C", rir=2),
        Gene(slug="barra_fixa", sets=3, tier="B", rir=2),
    ]
    risky_plan = [
        Gene(slug="rdl_terra_romeno", sets=5, tier="A", rir=0),
        Gene(slug="barra_fixa", sets=5, tier="A", rir=0),
    ]
    stress_context = {"avg_bjj_rpe": 8.5, "stressed_tags": ["lombar", "pegada"]}

    safe_score = evaluate_fitness(safe_plan, stress_context)
    risky_score = evaluate_fitness(risky_plan, stress_context)

    assert safe_score > risky_score


def test_evolve_microcycle_converges_to_high_fitness():
    context = {
        "avg_bjj_rpe": 9.0,
        "stressed_tags": ["lombar"],
        "exercises": ["agachamento_livre", "rdl_terra_romeno", "elevacao_pelvica"],
    }
    best_plan, best_score = evolve_microcycle(context, generations=30, pop_size=20, seed=42)

    assert len(best_plan) == 3
    assert best_score > 50.0
    rdl_gene = next(g for g in best_plan if g.slug == "rdl_terra_romeno")
    assert rdl_gene.tier == "C"
