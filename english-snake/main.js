/**
 * 简易英语学习贪吃蛇
 * - 画布渲染贪吃蛇
 * - 吃到食物后弹出单词卡（含音标、TTS 发音、例句）
 * - 本地存储分数、学习计数
 */

/** @typedef {{
 *  word: string,
 *  ipa?: string,
 *  definition: string,
 *  examples: string[],
 *  tts?: string
 * }} VocabItem */

/**
 * 迷你词库：可自由扩展。可接外部 API（如 Oxford/Cambridge）或自建 JSON。
 * 这里内置基础演示数据，并提供音标与示例。
 * 发音优先用 Web Speech API；若浏览器不支持，可使用 `tts` 字段音频 URL。
 * 音频 URL 可置空，保持降级可用。
 * @type {VocabItem[]}
 */
let VOCAB = [
  {
    word: "apple",
    ipa: "/ˈæp.əl/",
    definition: "a round fruit with red or green skin and a whitish inside",
    examples: [
      "She ate a juicy apple for breakfast.",
      "An apple a day keeps the doctor away.",
    ],
  },
  {
    word: "benevolent",
    ipa: "/bəˈnev.əl.ənt/",
    definition: "kind and helpful",
    examples: [
      "She was a benevolent leader who cared about her team.",
      "A benevolent smile spread across his face.",
    ],
  },
  {
    word: "catalyst",
    ipa: "/ˈkæt.əl.ɪst/",
    definition: "something that makes a chemical reaction happen more quickly; a person or thing that causes a change",
    examples: [
      "The new policy acted as a catalyst for innovation.",
      "Enzymes are biological catalysts.",
    ],
  },
  {
    word: "diligent",
    ipa: "/ˈdɪl.ɪ.dʒənt/",
    definition: "careful and using a lot of effort",
    examples: [
      "He is a diligent student who always finishes his homework.",
      "They worked with diligent attention to detail.",
    ],
  },
  {
    word: "empathy",
    ipa: "/ˈem.pə.θi/",
    definition: "the ability to share someone else's feelings or experiences",
    examples: [
      "Empathy helps build strong relationships.",
      "Nurses must show empathy towards patients.",
    ],
  },
  {
    word: "fragile",
    ipa: "/ˈfrædʒ.aɪl/",
    definition: "easily broken, damaged, or destroyed",
    examples: [
      "Please handle the fragile vase with care.",
      "Their relationship is still fragile after the argument.",
    ],
  },
  {
    word: "gratitude",
    ipa: "/ˈɡræt.ɪ.tjuːd/",
    definition: "the feeling or quality of being grateful",
    examples: [
      "She expressed her gratitude to her mentors.",
      "Keep a journal to cultivate gratitude.",
    ],
  },
];

/** 当前启用的活动词库（可被导入替换） */
let activeVocab = [...VOCAB];

// ---- DOM ----
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const resetBtn = document.getElementById("resetBtn");
const speedSelect = document.getElementById("speedSelect");
const importBtn = document.getElementById("importBtn");
const importInput = document.getElementById("importInput");
const helpBtn = document.getElementById("helpBtn");
const scoreEl = document.getElementById("score");
const bestScoreEl = document.getElementById("bestScore");
const learnedCountEl = document.getElementById("learnedCount");

// Modal
const modal = document.getElementById("wordModal");
const wordTitle = document.getElementById("wordTitle");
const wordIpa = document.getElementById("wordIpa");
const wordDef = document.getElementById("wordDef");
const examplesList = document.getElementById("examplesList");
const speakWordBtn = document.getElementById("speakWordBtn");
const speakExampleBtn = document.getElementById("speakExampleBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const nextBtn = document.getElementById("nextBtn");
// touch dpad
const dirUpBtn = document.getElementById("dirUp");
const dirDownBtn = document.getElementById("dirDown");
const dirLeftBtn = document.getElementById("dirLeft");
const dirRightBtn = document.getElementById("dirRight");
// help modal
const helpModal = document.getElementById("helpModal");
const closeHelpBtn = document.getElementById("closeHelpBtn");
const closeHelpFooterBtn = document.getElementById("closeHelpFooterBtn");

// ---- 游戏参数 ----
const CELL_SIZE = 20; // 网格大小
const GRID_COLS = Math.floor(canvas.width / CELL_SIZE);
const GRID_ROWS = Math.floor(canvas.height / CELL_SIZE);

/** @type {{x:number,y:number}[]} */
let snake = [];
/** @type {{x:number,y:number}} */
let food = { x: 10, y: 10 };
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let score = 0;
let bestScore = Number(localStorage.getItem("snake_best") || 0);
let learnedCount = Number(localStorage.getItem("snake_learned") || 0);
let timer = null;
let tickMs = Number(speedSelect.value);
let isPaused = true;

bestScoreEl.textContent = String(bestScore);
learnedCountEl.textContent = String(learnedCount);

// ---- 初始化与重置 ----
function initGame() {
  snake = [
    { x: 5, y: 10 },
    { x: 4, y: 10 },
    { x: 3, y: 10 },
  ];
  direction = { x: 1, y: 0 };
  nextDirection = { x: 1, y: 0 };
  score = 0;
  scoreEl.textContent = String(score);
  placeFood();
  draw();
  // 重置按钮状态
  if (startBtn) {
    startBtn.disabled = false;
    startBtn.classList.remove("disabled");
  }
}

/** 随机放置食物到空网格 */
function placeFood() {
  while (true) {
    const x = Math.floor(Math.random() * GRID_COLS);
    const y = Math.floor(Math.random() * GRID_ROWS);
    if (!snake.some((s) => s.x === x && s.y === y)) {
      food = { x, y };
      return;
    }
  }
}

// ---- 绘制 ----
function drawCell(x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1);
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // 背景网格微弱
  ctx.strokeStyle = "rgba(255,255,255,0.03)";
  for (let i = 0; i <= GRID_COLS; i++) {
    ctx.beginPath();
    ctx.moveTo(i * CELL_SIZE, 0);
    ctx.lineTo(i * CELL_SIZE, canvas.height);
    ctx.stroke();
  }
  for (let j = 0; j <= GRID_ROWS; j++) {
    ctx.beginPath();
    ctx.moveTo(0, j * CELL_SIZE);
    ctx.lineTo(canvas.width, j * CELL_SIZE);
    ctx.stroke();
  }

  // 食物
  drawCell(food.x, food.y, "#f59e0b");

  // 蛇
  snake.forEach((seg, idx) => {
    const color = idx === 0 ? "#22d3ee" : "#38bdf8";
    drawCell(seg.x, seg.y, color);
  });
}

// ---- 更新 ----
function tick() {
  if (isPaused) return;
  direction = nextDirection;
  const head = { x: snake[0].x + direction.x, y: snake[0].y + direction.y };

  // 撞墙
  if (head.x < 0 || head.x >= GRID_COLS || head.y < 0 || head.y >= GRID_ROWS) {
    gameOver();
    return;
  }
  // 撞自己
  if (snake.some((s) => s.x === head.x && s.y === head.y)) {
    gameOver();
    return;
  }

  snake.unshift(head);

  // 吃到食物
  if (head.x === food.x && head.y === food.y) {
    score += 1;
    scoreEl.textContent = String(score);
    if (score > bestScore) {
      bestScore = score;
      localStorage.setItem("snake_best", String(bestScore));
      bestScoreEl.textContent = String(bestScore);
    }
    placeFood();
    // 弹出学习卡片，暂停
    isPaused = true;
    showNextWord();
  } else {
    snake.pop();
  }

  draw();
}

function startLoop() {
  if (timer) clearInterval(timer);
  timer = setInterval(tick, tickMs);
}

function gameOver() {
  isPaused = true;
  toast("游戏结束，分数：" + score);
  // 游戏结束时禁用“开始”按钮
  if (startBtn) {
    startBtn.disabled = true;
    startBtn.classList.add("disabled");
  }
}

// ---- 输入 ----
window.addEventListener("keydown", (e) => {
  switch (e.key) {
    case "ArrowUp":
    case "w":
    case "W":
      if (direction.y !== 1) nextDirection = { x: 0, y: -1 };
      break;
    case "ArrowDown":
    case "s":
    case "S":
      if (direction.y !== -1) nextDirection = { x: 0, y: 1 };
      break;
    case "ArrowLeft":
    case "a":
    case "A":
      if (direction.x !== 1) nextDirection = { x: -1, y: 0 };
      break;
    case "ArrowRight":
    case "d":
    case "D":
      if (direction.x !== -1) nextDirection = { x: 1, y: 0 };
      break;
    case " ":
      isPaused = !isPaused;
      break;
  }
});

// 触控按钮
function bindDir(btn, vec){
  if(!btn) return;
  const on = (ev)=>{
    ev.preventDefault();
    if(Math.abs(vec.x)===1 && direction.x!==-vec.x){
      nextDirection = vec;
    } else if(Math.abs(vec.y)===1 && direction.y!==-vec.y){
      nextDirection = vec;
    }
  };
  btn.addEventListener("mousedown", on);
  btn.addEventListener("touchstart", on, {passive:false});
}
bindDir(dirUpBtn, {x:0,y:-1});
bindDir(dirDownBtn, {x:0,y:1});
bindDir(dirLeftBtn, {x:-1,y:0});
bindDir(dirRightBtn, {x:1,y:0});

// 触控滑动手势
let touchStart = null;
canvas.addEventListener("touchstart", (e)=>{
  const t = e.changedTouches[0];
  touchStart = {x:t.clientX,y:t.clientY};
}, {passive:true});
canvas.addEventListener("touchend", (e)=>{
  const t = e.changedTouches[0];
  if(!touchStart) return;
  const dx = t.clientX - touchStart.x;
  const dy = t.clientY - touchStart.y;
  const ax = Math.abs(dx), ay = Math.abs(dy);
  if(Math.max(ax,ay) < 24) return; // 忽略微小滑动
  if(ax>ay){
    if(dx>0 && direction.x!==-1) nextDirection={x:1,y:0};
    else if(dx<0 && direction.x!==1) nextDirection={x:-1,y:0};
  }else{
    if(dy>0 && direction.y!==-1) nextDirection={x:0,y:1};
    else if(dy<0 && direction.y!==1) nextDirection={x:0,y:-1};
  }
  touchStart = null;
}, {passive:true});

startBtn.addEventListener("click", () => {
  if (startBtn.disabled) return; // 禁用时不响应
  isPaused = false;
  if (!timer) startLoop();
});
pauseBtn.addEventListener("click", () => (isPaused = true));
resetBtn.addEventListener("click", () => {
  isPaused = true;
  initGame();
});
speedSelect.addEventListener("change", () => {
  tickMs = Number(speedSelect.value);
  startLoop();
});

// 导入词库（JSON）
importBtn && importBtn.addEventListener("click", () => importInput && importInput.click());
importInput && importInput.addEventListener("change", async () => {
  const file = importInput.files && importInput.files[0];
  if (!file) return;
  try {
    const text = await file.text();
    /** @type {VocabItem[] | {word:string, def?:string, ipa?:string, examples?:string[]}[]} */
    const data = JSON.parse(text);
    const normalized = (Array.isArray(data) ? data : []).map((d) => ({
      word: String(d.word || "").trim(),
      ipa: d.ipa || "",
      definition: (d.definition || d.def || "").trim(),
      examples: Array.isArray(d.examples) ? d.examples : [],
    })).filter((d) => d.word && d.definition);
    if (!normalized.length) {
      toast("词库为空或格式无效");
      return;
    }
    activeVocab = normalized;
    vocabIndex = 0;
    toast(`已导入词库，共 ${activeVocab.length} 条`);
  } catch (err) {
    console.error(err);
    toast("导入失败：JSON 解析错误");
  } finally {
    importInput.value = "";
  }
});

// 词库说明弹窗
helpBtn && helpBtn.addEventListener("click", () => {
  if (helpModal) helpModal.hidden = false;
});
const closeHelp = () => { if (helpModal) helpModal.hidden = true; };
closeHelpBtn && closeHelpBtn.addEventListener("click", closeHelp);
closeHelpFooterBtn && closeHelpFooterBtn.addEventListener("click", closeHelp);

// ---- 词卡弹窗 ----
let vocabIndex = 0;
function showNextWord() {
  const ref = activeVocab.length ? activeVocab : VOCAB;
  const item = ref[vocabIndex % ref.length];
  vocabIndex++;

  wordTitle.textContent = item.word;
  wordIpa.textContent = item.ipa || "";
  wordDef.textContent = item.definition;
  examplesList.innerHTML = "";
  for (const ex of item.examples) {
    const li = document.createElement("li");
    li.textContent = ex;
    examplesList.appendChild(li);
  }

  modal.hidden = false;
  speak(item.word);
}

closeModalBtn.addEventListener("click", () => {
  modal.hidden = true;
});
nextBtn.addEventListener("click", () => {
  modal.hidden = true;
  learnedCount += 1;
  localStorage.setItem("snake_learned", String(learnedCount));
  learnedCountEl.textContent = String(learnedCount);
  isPaused = false;
});

speakWordBtn.addEventListener("click", () => {
  const text = wordTitle.textContent || "";
  speak(text);
});

speakExampleBtn.addEventListener("click", () => {
  const first = examplesList.querySelector("li");
  if (first) speak(first.textContent || "");
});

// ---- TTS ----
/** 使用 Web Speech API 发音，若不可用则静默失败。 */
function speak(text) {
  const synth = window.speechSynthesis;
  if (!synth) return;
  const utter = new SpeechSynthesisUtterance(text);
  // 优先英语
  utter.lang = "en-US";
  utter.rate = 0.95;
  utter.pitch = 1.0;
  synth.cancel();
  synth.speak(utter);
}

// ---- 提示 ----
let toastTimer = null;
function toast(message) {
  let el = document.querySelector(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.style.opacity = "1";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 400);
  }, 1800);
}

// 启动
initGame();
startLoop();


