# Agent-Based Prosumer Model Example

## Introduction

This example demonstrates how the **CESDM Toolbox** can be extended with
an **Agent-Based Modelling (ABM)** layer. While the CESDM core schema
describes the physical electricity system, the additional
`schemas_agentbased` extension introduces socio-economic actors and
behavioural decision making.

The result is a single integrated CESDM model containing:

-   physical electricity infrastructure,
-   households,
-   distributed energy resources,
-   local energy communities,
-   autonomous decision-making agents, and
-   an agent-based simulation scenario.

------------------------------------------------------------------------

# Example Workflow

The example follows six major steps.

## Step 1 -- Load Multiple Schemas

The model is created using both the standard CESDM schema and the
agent-based extension.

``` python
schema_dir = REPO_ROOT / "schemas"
schema_agent_based_dir = REPO_ROOT / "schemas_agentbased"

model = build_model_from_yaml([
    schema_dir,
    schema_agent_based_dir,
])
```

This demonstrates the toolbox's capability to merge multiple schema
folders into one coherent data model.

------------------------------------------------------------------------

## Step 2 -- Create or Import the Base Electricity System

The script supports two workflows.

### Option A -- Import an Existing CESDM Model

``` bash
python example_agent_based_prosumer_model.py \
    --input existing_model.yaml
```

The existing infrastructure becomes the basis for the agent-based
extension.

### Option B -- Automatically Generate a Demonstration Network

If no input model is supplied, the example creates:

-   one geographical region,
-   one electricity carrier,
-   one renewable solar resource,
-   one low-voltage electrical bus.

This keeps the example completely self-contained.

------------------------------------------------------------------------

## Step 3 -- Build the Social Layer

The script creates entities representing the local community.

Hierarchy:

    Canton
       │
    Municipality
       │
    Energy Community
       │
    Households

Relationships are added using semantic CESDM relations such as:

-   `isPartOf`
-   `locatedIn`
-   `memberOf`

------------------------------------------------------------------------

## Step 4 -- Create Households and Physical Assets

Three households are generated.

Each household contains different characteristics including:

-   occupants
-   building type
-   ownership status
-   annual electricity demand
-   rooftop PV capacity
-   battery capacity
-   behavioural preferences

For every household the corresponding physical assets are created.

Possible assets include:

-   DemandUnit
-   GenerationUnit
-   StorageUnit

Ownership is explicitly represented inside the CESDM graph.

------------------------------------------------------------------------

## Step 5 -- Create Behavioural Agents

Each household receives its own **ProsumerAgent**.

The agent stores behavioural parameters such as:

-   risk aversion
-   price sensitivity
-   environmental preference
-   comfort preference
-   PV adoption probability
-   battery adoption probability
-   EV adoption probability

The agent controls the physical assets owned by its household.

Information available to agents includes:

-   electricity prices
-   PV subsidies
-   solar availability

This separation between physical assets and behavioural agents is a key
concept of the example.

------------------------------------------------------------------------

## Step 6 -- Community Aggregator

A higher-level **AggregatorAgent** coordinates all distributed assets.

Responsibilities include:

-   managing the local energy community,
-   observing market signals,
-   controlling distributed resources,
-   increasing community self-consumption.

The aggregator demonstrates how individual agents can be coordinated
while still preserving household autonomy.

------------------------------------------------------------------------

# Time-Series Profiles

Three example profiles are created.

  Profile              Purpose
  -------------------- ------------------------------
  Retail tariff        Electricity price signal
  PV subsidy           Investment incentive
  Solar availability   Renewable generation profile

These profiles influence agent decisions during simulation.

------------------------------------------------------------------------

# Agent-Based Simulation Scenario

Finally, an `AgentBasedModel` entity is created.

The scenario specifies:

-   simulation period (2025--2030),
-   yearly time step,
-   random seed,
-   optimisation objective.

All agents and controlled assets are linked to this simulation object.

------------------------------------------------------------------------

# Validation

Before export the model is validated.

``` python
errors = model.validate()
```

Only valid CESDM models are exported.

------------------------------------------------------------------------

# Output

The script exports both YAML and Frictionless representations.

    output/
    └── agent_based_model/
        ├── yaml/
        │   └── agent_based_prosumer_model.yaml
        └── frictionless/

------------------------------------------------------------------------

# Concepts Demonstrated

This example illustrates how CESDM can combine:

-   semantic data modelling,
-   electrical infrastructure,
-   distributed energy resources,
-   social entities,
-   behavioural economics,
-   agent-based modelling,
-   interoperable data exchange.

It is intended as a comprehensive reference for integrating agent-based
simulations into CESDM-based energy system models.
