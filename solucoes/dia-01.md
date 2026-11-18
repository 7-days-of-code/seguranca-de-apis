\# Dia 1 – Invadindo o Banco Pop

\## Relatório de identificação de vulnerabilidades em APIs



\### 1. Objetivo



Identificar falhas de segurança na API do Banco Pop, explorando possíveis problemas de autenticação e autorização que permitam o acesso indevido a informações de outros usuários e funcionalidades administrativas.



\### 2. Metodologia



Os testes foram realizados com o usuário Bruno autenticado na API. A partir dessa sessão, foram executadas requisições para consultar informações de outros usuários e acessar funcionalidades administrativas.



O objetivo foi verificar se a aplicação validava corretamente as permissões de acesso de acordo com o usuário autenticado.



\### 4. Vulnerabilidades identificadas



\#### 4.1. Acesso indevido ao extrato de outro usuário



\- \*\*Rota:\*\* `GET /extratos/1`

\- \*\*Usuário autenticado:\*\* bruno.

\- \*\*Informação exposta:\*\* Lançamento bancário da ana, com a descrição "salário".

\- \*\*Resultado:\*\* A API permitiu consultar um lançamento que não pertencia ao usuário autenticado.

\- \*\*Classificação OWASP:\*\* API1 – Broken Object Level Authorization (BOLA).



\*\*Análise:\*\* A aplicação não verificou se o lançamento solicitado pertencia ao usuário autenticado, permitindo o acesso indevido a informações financeiras de terceiros.



\#### 4.2. Acesso indevido ao saldo bancário de outro usuário



\- \*\*Rota:\*\* `GET /contas/1/saldo`

\- \*\*Usuário autenticado:\*\* bruno.

\- \*\*Informação exposta:\*\* Saldo bancário da ana, no valor de R$ 1.200,00.

\- \*\*Resultado:\*\* A API permitiu consultar o saldo de uma conta pertencente a outro usuário.

\- \*\*Classificação OWASP:\*\* API1 – Broken Object Level Authorization (BOLA).



\*\*Análise:\*\* A aplicação não realizou a validação adequada da titularidade da conta antes de disponibilizar informações financeiras.



\#### 4.3. Exposição de dados pessoais e credenciais



\- \*\*Rota:\*\* `GET /usuarios/1`

\- \*\*Usuário autenticado:\*\* bruno.

\- \*\*Informações expostas:\*\* E-mail, papel do usuário e senha da bna (`ana123`) em texto puro.

\- \*\*Resultado:\*\* A API disponibilizou informações pessoais e credenciais de outro usuário.

\- \*\*Classificação OWASP:\*\* API1 + API3.



\*\*Análise:\*\* Além de permitir a consulta de dados de outro usuário, a aplicação expôs uma senha em texto puro, comprometendo a confidencialidade das credenciais.



\#### 4.4. Acesso indevido a funcionalidades administrativas



\- \*\*Rota:\*\* `GET /admin/usuarios`

\- \*\*Usuário autenticado:\*\* bruno (perfil cliente).

\- \*\*Informações expostas:\*\* Dados de todas as contas cadastradas, incluindo senhas e saldos.

\- \*\*Resultado:\*\* bruno conseguiu acessar informações administrativas mesmo sem possuir perfil de administrador.

\- \*\*Classificação OWASP:\*\* API5 – Broken Function Level Authorization (BFLA) + API3.



\*\*Análise:\*\* A aplicação não restringiu adequadamente o acesso à funcionalidade administrativa, permitindo que um usuário comum consultasse informações que deveriam estar disponíveis somente para usuários autorizados.



\### 5. Resumo dos resultados



| Rota | Usuário autenticado | Informação exposta | Risco OWASP |

|---|---|---|---|

| `GET /extratos/1` | Bruno | Lançamento "salário" da Ana | API1 (BOLA) |

| `GET /contas/1/saldo` | Bruno | Saldo da Ana (R$ 1.200,00) | API1 (BOLA) |

| `GET /usuarios/1` | Bruno | E-mail, papel e senha em texto puro | API1 + API3 |

| `GET /admin/usuarios` | Bruno (cliente) | Todas as contas, com senhas e saldos | API5 (BFLA) + API3 |



\### 6. Conclusão



Os testes demonstraram que a API do Banco Pop apresenta falhas importantes de autorização e proteção de dados.



Mesmo autenticado com um perfil de cliente, Bruno conseguiu acessar informações financeiras de outra usuária, consultar dados pessoais e credenciais e acessar uma funcionalidade administrativa.



A atividade evidenciou que a autenticação, isoladamente, não garante a segurança de uma API. É necessário implementar controles de autorização que verifiquem tanto a titularidade dos recursos quanto o nível de privilégio de cada usuário.



Nesta primeira etapa, as vulnerabilidades foram identificadas, exploradas em ambiente de testes e documentadas, sem alterações no código-fonte da aplicação, como solicitado no desafio.

