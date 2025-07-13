const DART_TOKEN = process.env.DART_TOKEN;

const DART_ROOT_URL = "https://app.dartai.com/api/v0";
const DART_REPLICATE_SPACE_URL = `${DART_ROOT_URL}/spaces/replicate`;
const DART_CREATE_TRANSACTION_URL = `${DART_ROOT_URL}/transactions/create`;

const DUID_CHARS = Array.from(Array(26).keys())
  .map((i) => String.fromCharCode(i + 65))
  .concat(Array.from(Array(26).keys()).map((i) => String.fromCharCode(i + 97)))
  .concat(Array.from(Array(10).keys()).map((i) => `${i}`))
  .concat(["-", "_"])
  .sort();

const randomSample = (arr, k = 1) => Array.from(Array(k), () => arr[Math.floor(Math.random() * arr.length)]);

const makeDuid = () => randomSample(DUID_CHARS, 12).join("");

const clientDuid = makeDuid();

const replicateSpace = async (duid, title) => {
  const response = await fetch(`${DART_REPLICATE_SPACE_URL}/${duid}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${DART_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
    }),
  });
  return response.json();
};

const updateDartboard = async (duid, title) => {
  const response = await fetch(`${DART_CREATE_TRANSACTION_URL}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${DART_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      clientDuid,
      items: [
        {
          duid: makeDuid(),
          operations: [
            {
              model: "dartboard",
              kind: "update",
              data: {
                duid,
                title,
              },
            },
          ],
          kind: "dartboard_update",
        },
      ],
    }),
  });
  return response.json();
};

const createTask = async (dartboardDuid, title) => {
  const response = await fetch(`${DART_CREATE_TRANSACTION_URL}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${DART_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      clientDuid,
      items: [
        {
          duid: makeDuid(),
          operations: [
            {
              model: "task",
              kind: "create",
              data: {
                duid: makeDuid(),
                dartboardDuid,
                title,
              },
            },
          ],
          kind: "task_create",
        },
      ],
    }),
  });
  return response.json();
};

const main = async () => {
  const replicatedSpaceDuid = (await replicateSpace("Mp9fFrctHssQ", "New space title")).duid;
  const updatedDartboard = (await updateDartboard("8ytNh7Aa5weF", "New dartboard title")).results[0].models;
  const createdTask = (await createTask("8ytNh7Aa5weF", "New task title")).results[0].models;
  console.log(replicatedSpaceDuid, updatedDartboard, createdTask);
};

main();
