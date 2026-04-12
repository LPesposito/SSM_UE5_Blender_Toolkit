# Scene StaticMesh - UE5 Workflow Toolkit

Um addon profissional para Blender projetado para automatizar a organização e exportação de cenas complexas ou Static Meshes individuais para a Unreal Engine 5. Garante padrões de nomenclatura da indústria, colisões otimizadas e alinhamento perfeito de coordenadas.

---

## Descrição (Pipeline Blender ➔ UE5)
Este toolkit foi desenvolvido para eliminar os gargalos técnicos comuns ao mover assets para a **UE5**. Ele foca em garantir que o que você vê no Blender seja exatamente o que você recebe na Unreal, automatizando tarefas repetitivas de pivotagem, colisão e nomenclatura que costumam causar erros de importação ou problemas de performance física.

---

## Funcionalidades

### 1. Geometria e Pivô de Precisão
* **Snap de Pivô Avançado:** Define a origem para a Base (Piso), Centro, Esquerda, Direita, Frente ou Trás.
* **Exportação na Origem Zero:** No modo Individual, o script move temporariamente cada objeto para (0,0,0) durante a exportação, garantindo que o pivô na Unreal coincida exatamente com a sua configuração no Blender.
* **Fix Transforms:** Aplica escala e rotação mantendo a integridade geométrica.

### 2. Colisões Automatizadas (UCX/UBX)
* **Smart Convex (UCX):** Gera invólucros convexos simplificados (redução de 50% nos polígonos) para otimização de performance.
* **Simple Box (UBX):** Cria colisores de caixa perfeitos baseados no Bounding Box do objeto.
* **Compound Box (Multi):** Separa malhas complexas em partes soltas e gera caixas UBX individuais para cada parte, tudo parentado automaticamente.

### 3. Materiais e Nomenclatura de Texturas
* **Suporte Multi-Material:** Gerencia objetos com múltiplos slots seguindo o padrão `M_[NomeObjeto]_[NomeMaterial]`.
* **Prevenção de Duplicatas:** Rastreia materiais já processados para evitar renomeações redundantes ou conflitos de dados.
* **Padronização de Texturas:** Analisa os nós do Principled BSDF e renomeia imagens para `T_[NomeMaterial]_[Sufixo]` (ex: `T_Parede_Tijolo_Normal`).

### 4. Exportação Otimizada para UE5
* **Correção de Eixos:** Configurações nativas de exportação com -Z Forward e Y Up.
* **Exportação em Lote Individual:** Exporta cada malha selecionada como um arquivo FBX único, incluindo automaticamente seus respectivos objetos de colisão.
* **Conversor de Luz:** Multiplica a intensidade das luzes do Blender para os valores físicos da Unreal.

---

## Instalação

1. Baixe este repositório como um arquivo **ZIP**.
2. No Blender, vá em: **Edit > Preferences > Add-ons > Install**.
3. Selecione o arquivo ZIP e ative o addon **Import-Export: SSM - UE5 Workflow Toolkit**.
4. O painel aparecerá na **Sidebar (N)** na aba **UE5 Export**.

---

## Uso

O addon está dividido em 4 etapas lógicas:

1. **1. Visualization:** Alterna o *Backface Culling* para encontrar faces invertidas antes da exportação.
2. **2. Geometry Setup:** Onde você define a posição do pivô, corrige transformações e gera colisões (UCX/UBX) com o método escolhido.
3. **3. Materials & Textures:** Padroniza internamente todos os nomes de materiais e texturas e permite salvar as imagens em uma pasta dedicada no disco.
4. **4. Export:** Ajusta a intensidade das luzes e define se a cena será exportada como um grupo único ou como assets individuais.

---

## Créditos
Desenvolvido por **Lp Moonkey Dev**.

---
*Nota: Este addon utiliza bmesh para operações geométricas avançadas e suporta traduções nativas do Blender (PT-BR).*