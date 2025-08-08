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
const settingsBtn = document.getElementById("settingsBtn");
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
// settings modal
const settingsModal = document.getElementById("settingsModal");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const saveSettingsBtn = document.getElementById("saveSettingsBtn");
const themeSelect = document.getElementById("themeSelect");
const contrastToggle = document.getElementById("contrastToggle");
const reducedMotionToggle = document.getElementById("reducedMotionToggle");
const voiceAccent = document.getElementById("voiceAccent");
const voiceRate = document.getElementById("voiceRate");
const voicePitch = document.getElementById("voicePitch");
const sfxToggle = document.getElementById("sfxToggle");
const bgmToggle = document.getElementById("bgmToggle");

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
let lastTime = performance.now();
let settings = loadSettings();
applyTheme(settings.theme, settings.highContrast);
syncSettingsUI();

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
      foodHue = hashHue((activeVocab[vocabIndex % Math.max(1, activeVocab.length)]?.word) || "food");
      return;
    }
  }
}

// ---- 绘制 ----
function drawCell(x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1);
}

// 渲染参数与元素
let particles = [];
let foodHue = 45;

/** 生成吃到食物时的光点粒子 */
function spawnParticles(cx, cy) {
  const centerX = cx * CELL_SIZE + CELL_SIZE / 2;
  const centerY = cy * CELL_SIZE + CELL_SIZE / 2;
  for (let i = 0; i < 24; i++) {
    const angle = (Math.PI * 2 * i) / 24 + Math.random() * 0.3;
    const speed = 1.2 + Math.random() * 1.4;
    particles.push({
      x: centerX,
      y: centerY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1.0,
      hue: foodHue,
    });
  }
}

function updateParticles(dt) {
  for (const p of particles) {
    p.x += p.vx * dt * 60 * 0.016;
    p.y += p.vy * dt * 60 * 0.016;
    p.vx *= 0.98;
    p.vy *= 0.98;
    p.life -= dt * 1.6;
  }
  particles = particles.filter((p) => p.life > 0);
}

function drawFoodOrb(x, y, t) {
  const cx = x * CELL_SIZE + CELL_SIZE / 2;
  const cy = y * CELL_SIZE + CELL_SIZE / 2;
  const r = CELL_SIZE * (0.42 + Math.sin(t * 2) * 0.03);
  const g = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.4, r * 0.2, cx, cy, r);
  g.addColorStop(0, `hsla(${foodHue}, 85%, 65%, .95)`);
  g.addColorStop(0.6, `hsla(${foodHue}, 85%, 55%, .85)`);
  g.addColorStop(1, `hsla(${foodHue}, 85%, 40%, .65)`);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fill();
  // 高光
  ctx.fillStyle = "rgba(255,255,255,.35)";
  ctx.beginPath();
  ctx.ellipse(cx - r * 0.25, cy - r * 0.35, r * 0.18, r * 0.12, -0.6, 0, Math.PI * 2);
  ctx.fill();
}

function drawSnake(t) {
  // 尾部到头部绘制，使用渐变与轻微光晕
  for (let i = snake.length - 1; i >= 0; i--) {
    const seg = snake[i];
    const cx = seg.x * CELL_SIZE + CELL_SIZE / 2;
    const cy = seg.y * CELL_SIZE + CELL_SIZE / 2;
    const r = CELL_SIZE * (i === 0 ? 0.48 : 0.44);
    const hue = 190 + (i / snake.length) * 40;
    const grad = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.35, r * 0.15, cx, cy, r);
    grad.addColorStop(0, `hsla(${hue}, 90%, 70%, .95)`);
    grad.addColorStop(0.7, `hsla(${hue}, 90%, 55%, .9)`);
    grad.addColorStop(1, `hsla(${hue}, 90%, 40%, .85)`);
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();

    // 微光晕
    ctx.strokeStyle = `hsla(${hue}, 95%, 70%, .18)`;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(cx, cy, r + 2, 0, Math.PI * 2);
    ctx.stroke();
  }

  // 眼睛（头部）
  const head = snake[0];
  if (head) {
    const hx = head.x * CELL_SIZE + CELL_SIZE / 2;
    const hy = head.y * CELL_SIZE + CELL_SIZE / 2;
    const eyeOffset = CELL_SIZE * 0.18;
    ctx.fillStyle = "#0b1020";
    ctx.beginPath();
    ctx.arc(hx - eyeOffset, hy - 2, 3, 0, Math.PI * 2);
    ctx.arc(hx + eyeOffset, hy - 2, 3, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.fillStyle = `hsla(${p.hue}, 90%, 70%, ${Math.max(0, p.life)})`;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 2.2, 0, Math.PI * 2);
    ctx.fill();
  }
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

  // 食物（发光球）
  drawFoodOrb(food.x, food.y, performance.now() / 1000);

  // 蛇（渐变圆段）
  drawSnake(performance.now() / 1000);

  // 粒子
  drawParticles();
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
    // 粒子特效
    spawnParticles(food.x, food.y);
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

// 设置面板弹窗
settingsBtn && settingsBtn.addEventListener("click", () => openModal(settingsModal));
closeSettingsBtn && closeSettingsBtn.addEventListener("click", () => closeModal(settingsModal));
saveSettingsBtn && saveSettingsBtn.addEventListener("click", () => {
  settings = {
    theme: themeSelect.value,
    highContrast: Boolean(contrastToggle.checked),
    reducedMotion: Boolean(reducedMotionToggle.checked),
    accent: voiceAccent.value,
    rate: Number(voiceRate.value),
    pitch: Number(voicePitch.value),
    sfx: Boolean(sfxToggle.checked),
    bgm: Boolean(bgmToggle.checked),
  };
  saveSettings(settings);
  applyTheme(settings.theme, settings.highContrast);
  closeModal(settingsModal);
  toast("设置已保存");
});

// 即时预览并持久化
function bindLiveSettings() {
  if (themeSelect) themeSelect.addEventListener("change", () => { settings.theme = themeSelect.value; saveSettings(settings); applyTheme(settings.theme, settings.highContrast); });
  if (contrastToggle) contrastToggle.addEventListener("change", () => { settings.highContrast = contrastToggle.checked; saveSettings(settings); applyTheme(settings.theme, settings.highContrast); document.body.classList.toggle('contrast', settings.highContrast); });
  if (reducedMotionToggle) reducedMotionToggle.addEventListener("change", () => { settings.reducedMotion = reducedMotionToggle.checked; saveSettings(settings); document.body.style.setProperty('animation-duration', settings.reducedMotion ? '0s' : ''); });
  if (voiceAccent) voiceAccent.addEventListener("change", () => { settings.accent = voiceAccent.value; saveSettings(settings); });
  if (voiceRate) voiceRate.addEventListener("input", () => { settings.rate = Number(voiceRate.value); saveSettings(settings); });
  if (voicePitch) voicePitch.addEventListener("input", () => { settings.pitch = Number(voicePitch.value); saveSettings(settings); });
  if (sfxToggle) sfxToggle.addEventListener("change", () => { settings.sfx = sfxToggle.checked; saveSettings(settings); });
  if (bgmToggle) bgmToggle.addEventListener("change", () => { settings.bgm = bgmToggle.checked; saveSettings(settings); });
}
bindLiveSettings();

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

  openModal(modal);
  speak(item.word);
}

closeModalBtn.addEventListener("click", () => closeModal(modal));
nextBtn.addEventListener("click", () => {
  closeModal(modal);
  learnedCount += 1;
  localStorage.setItem("snake_learned", String(learnedCount));
  learnedCountEl.textContent = String(learnedCount);
  isPaused = false;
});

// 再练一下（提升该词再次出现权重）
const againBtn = document.getElementById("againBtn");
againBtn && againBtn.addEventListener("click", () => {
  closeModal(modal);
  // 将当前词放入队列后面两次，简单提高再现概率
  const ref = activeVocab.length ? activeVocab : VOCAB;
  const lastIndex = (vocabIndex - 1 + ref.length) % ref.length;
  const item = ref[lastIndex];
  if (activeVocab === ref) {
    activeVocab.splice(vocabIndex, 0, item, item);
  }
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
  utter.lang = settings.accent || "en-US";
  utter.rate = Number(settings.rate || 0.95);
  utter.pitch = Number(settings.pitch || 1.0);
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

// ---- Modal 开关 ----
function openModal(el){
  if(!el) return;
  el.hidden = false;
  el.classList.remove("closing");
  el.classList.add("open");
}
function closeModal(el){
  if(!el) return;
  el.classList.remove("open");
  el.classList.add("closing");
  setTimeout(()=>{ el.hidden = true; el.classList.remove("closing"); }, 180);
}

// ---- 渲染循环（用于粒子与食物呼吸动效） ----
function renderLoop(now){
  const dt = Math.min(0.05, (now - lastTime) / 1000);
  lastTime = now;
  updateParticles(dt);
  draw();
  requestAnimationFrame(renderLoop);
}

// 启动
initGame();
startLoop();
requestAnimationFrame(renderLoop);

// ---- 辅助：根据单词生成稳定色相 ----
function hashHue(str){
  let h = 0;
  for(let i=0;i<str.length;i++){ h = (h*31 + str.charCodeAt(i)) >>> 0; }
  return 180 + (h % 120); // 蓝绿到粉紫区间
}

// ---- 设置存取与主题应用 ----
function loadSettings(){
  try{
    const raw = localStorage.getItem("snake_settings");
    return raw ? JSON.parse(raw) : {theme:"dark", highContrast:false, reducedMotion:false, accent:"en-US", rate:0.95, pitch:1.0, sfx:true, bgm:false};
  }catch{ return {theme:"dark", highContrast:false, reducedMotion:false, accent:"en-US", rate:0.95, pitch:1.0, sfx:true, bgm:false}; }
}
function saveSettings(s){ localStorage.setItem("snake_settings", JSON.stringify(s)); }
function applyTheme(theme, highContrast){
  const body = document.body;
  const useLight = theme === "light" || (theme === "auto" && matchMedia('(prefers-color-scheme: light)').matches);
  body.classList.toggle("light", useLight);
  // 高对比下仅增强对比度，不直接覆盖文字颜色，避免暗色主题被误改
  if (highContrast) {
    body.style.setProperty('--panel', useLight ? '#ffffff' : '#0b1220');
    body.style.setProperty('--panel-2', useLight ? '#f3f4f6' : '#0e1426');
  } else {
    body.style.removeProperty('--panel');
    body.style.removeProperty('--panel-2');
  }
  body.classList.toggle('contrast', !!highContrast);
}

// PWA 注册
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js').catch(()=>{});
}

function syncSettingsUI(){
  if (themeSelect) themeSelect.value = settings.theme || 'dark';
  if (contrastToggle) contrastToggle.checked = !!settings.highContrast;
  if (reducedMotionToggle) reducedMotionToggle.checked = !!settings.reducedMotion;
  if (voiceAccent) voiceAccent.value = settings.accent || 'en-US';
  if (voiceRate) voiceRate.value = String(settings.rate || 0.95);
  if (voicePitch) voicePitch.value = String(settings.pitch || 1.0);
  if (sfxToggle) sfxToggle.checked = !!settings.sfx;
  if (bgmToggle) bgmToggle.checked = !!settings.bgm;
}

// 自动主题监听（当选择“自动”时）
const media = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)');
if (media && typeof media.addEventListener === 'function') {
  media.addEventListener('change', () => { if ((settings.theme||'dark') === 'auto') applyTheme('auto', settings.highContrast); });
}


