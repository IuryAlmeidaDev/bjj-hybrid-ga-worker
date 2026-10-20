# 🧬 BJJ Hybrid Genetic Algorithm Worker (Python)

Motor de **Algoritmo Genético Evolutivo** em Python para otimização de microciclos de musculação em praticantes de **Jiu-Jítsu**.

## 🧠 Como Funciona a Otimização Genética

1. **Gene (`Gene`):** Representa a prescrição de um exercício (`slug`, `sets` de 2 a 5, `tier` entre `'A'`, `'B'` ou `'C'`, e `rir` de 0 a 3).
2. **Cromossomo:** Conjunto completo de exercícios de uma sessão de treino.
3. **Função de Aptidão (`evaluate_fitness`):**
   - Recompensa o volume ótimo por sessão.
   - Penaliza severamente treinos até a falha (`RIR < 2`) ou com volume excessivo quando o RPE médio do Jiu-Jítsu é alto ($\ge 8$).
   - Premia a seleção automática das alternativas protetoras (`Tier B` ou `Tier C`) quando há desgaste sinalizado em `lombar`, `ombro` ou `pegada`.
4. **Operadores Evolutivos:** Elitismo (top 4 indivíduos preservados), cruzamento de ponto único (`crossover`) e mutação controlada (`mutate`).

## 🧪 Como Rodar os Testes

```bash
pip install -r requirements.txt
pytest test_optimizer.py -v
```
