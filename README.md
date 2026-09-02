# VirtuJudge documentation

This repository is the planning and design source for VirtuJudge. VirtuJudge helps teams practise a pitch, review measurable delivery signals, answer grounded follow-up questions, and receive evidence-linked team and individual feedback.

The current delivery target is a ten-day competition MVP. Production hardening and larger product ideas are recorded separately so they don't silently enter the MVP.

## Start here

- [Product scope](./Product/Scope.md)
- [Requirements and success measures](./Product/Requirements.md)
- [Risks and evidence gaps](./Product/Risks-and-Evidence-Gaps.md)
- [Domain language](./CONTEXT.md)
- [User-story map](./Product/User-Stories/README.md)
- [System architecture](./Architecture/System-Architecture.md)
- [Backend architecture](./Architecture/Backend-Architecture.md)
- [AI/ML architecture](./Architecture/AI-ML-Architecture.md)
- [Technology stack](./Architecture/Technology-Stack.md)
- [Security, privacy, and retention](./Architecture/Security-Privacy-and-Retention.md)
- [Frontend/backend API](./Contracts/Frontend-Backend-API.md)
- [Backend/AI contract](./Contracts/Backend-AI-Contract.md)
- [Job and notification catalogue](./Contracts/Event-Catalogue.md)
- [Data contracts](./Contracts/Data-Contracts.md)
- [Ten-day delivery plan](./Planning/10-Day-Delivery-Plan.md)
- [Testing and quality plan](./Planning/Testing-and-Quality.md)
- [Review workflow](./Planning/Review-Workflow.md)
- [Documentation review](./Planning/Documentation-Review.md)
- [Future work](./Planning/Future-Work.md)
- [Repository bootstrap](./Planning/Repository-Bootstrap.md)
- [Architecture decisions](./adr/README.md)

## Source material

- [Original proposal](./Proposal/VirtuJudge-Proposal.md)
- `Proposal/VirtuJudge-Proposal.pdf`
- `Presentations/Presentation.pdf`

The proposal is the source of the product idea. The documents linked above resolve ambiguities in it and define the plan that should be reviewed before implementation starts.

## Documentation rules

1. Change the contract or decision document before changing behaviour.
2. Keep diagrams and examples consistent with the written contract.
3. Record hard-to-reverse decisions as ADRs.
4. Run the documentation and contract checks before requesting review.
5. Do not merge reviewed contract snapshots by hand when they can be generated from a service-owned schema.
