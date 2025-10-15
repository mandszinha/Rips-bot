# Discord TikTok Verification Bot

Bot para verificar se um usuário segue um TikTok específico e atribuir uma role no Discord.

## Como usar

1. Clone o repositório no Replit ou local:
git clone SEU_REPOSITORIO.git

markdown
Copiar código

2. Instale dependências:
pip install -r requirements.txt
playwright install

markdown
Copiar código

3. Configure o `config.py` com:
- TOKEN do Discord
- TIKTOK_USER (usuário a ser verificado)
- ROLE_NAME (nome da role que será atribuída)

4. Rode o bot:
python main.py

yaml
Copiar código

5. No Discord, use o comando:
!verificar @usuario

yaml
Copiar código
ou sem mencionar ninguém para verificar você mesmo:
!verificar
