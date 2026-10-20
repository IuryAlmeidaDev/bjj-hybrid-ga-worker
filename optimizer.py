from dataclasses import dataclass, asdict
import random
from typing import List, Dict, Any, Tuple


@dataclass
class Gene:
    slug: str
    sets: int        # 2 to 5
    tier: str        # 'A' (Primary), 'B' (Alt 1), 'C' (Alt 2)
    rir: int         # 1 to 3


def evaluate_fitness(chromosome: List[Gene], context: Dict[str, Any]) -> float:
    avg_rpe = float(context.get("avg_bjj_rpe", 6.0))
    stressed_tags = set(context.get("stressed_tags", []))

    score = 100.0
    total_sets = sum(g.sets for g in chromosome)

    # Optimal volume reward (9 to 12 sets per session for 3 exercises)
    if 8 <= total_sets <= 12:
        score += 20.0
    else:
        score -= abs(total_sets - 10) * 5.0

    for gene in chromosome:
        # High BJJ RPE requires RIR >= 2 and moderate sets
        if avg_rpe >= 8.0:
            if gene.rir < 2:
                score -= 25.0
            if gene.sets > 4:
                score -= 15.0
            if gene.sets == 3 and gene.rir == 2:
                score += 10.0

        # Joint protection rules
        if "lombar" in stressed_tags and gene.slug in ("rdl_terra_romeno", "remada_curvada"):
            if gene.tier == "C":
                score += 25.0
            elif gene.tier == "A":
                score -= 35.0

        if "pegada" in stressed_tags and gene.slug in ("barra_fixa", "farmers_walk"):
            if gene.tier in ("B", "C"):
                score += 15.0
            else:
                score -= 25.0

        if "ombro" in stressed_tags and gene.slug in ("supino_reto", "desenvolvimento_halteres"):
            if gene.tier in ("B", "C"):
                score += 15.0
            else:
                score -= 20.0

    return round(score, 4)


def random_gene(slug: str, rng: random.Random) -> Gene:
    return Gene(
        slug=slug,
        sets=rng.choice([2, 3, 4, 5]),
        tier=rng.choice(["A", "B", "C"]),
        rir=rng.choice([0, 1, 2, 3]),
    )


def crossover(parent1: List[Gene], parent2: List[Gene], rng: random.Random) -> List[Gene]:
    if len(parent1) < 2:
        return [Gene(**asdict(g)) for g in parent1]
    cut = rng.randint(1, len(parent1) - 1)
    child = [Gene(**asdict(g)) for g in parent1[:cut]] + [Gene(**asdict(g)) for g in parent2[cut:]]
    return child


def mutate(chromosome: List[Gene], rng: random.Random, mutation_rate: float = 0.25) -> List[Gene]:
    mutated = []
    for g in chromosome:
        if rng.random() < mutation_rate:
            mutated.append(random_gene(g.slug, rng))
        else:
            mutated.append(Gene(**asdict(g)))
    return mutated


def evolve_microcycle(
    context: Dict[str, Any],
    generations: int = 40,
    pop_size: int = 24,
    seed: int | None = None,
) -> Tuple[List[Gene], float]:
    rng = random.Random(seed)
    exercises: List[str] = context.get("exercises", [])

    population: List[List[Gene]] = [
        [random_gene(slug, rng) for slug in exercises]
        for _ in range(pop_size)
    ]

    for _ in range(generations):
        scored = [( evaluate_fitness(ind, context), ind ) for ind in population]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Elitism: keep top 4
        next_gen = [ind for _, ind in scored[:4]]

        while len(next_gen) < pop_size:
            p1 = rng.choice(scored[:10])[1]
            p2 = rng.choice(scored[:10])[1]
            child = crossover(p1, p2, rng)
            child = mutate(child, rng)
            next_gen.append(child)

        population = next_gen

    final_scored = [(evaluate_fitness(ind, context), ind) for ind in population]
    final_scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_plan = final_scored[0]
    return best_plan, best_score
