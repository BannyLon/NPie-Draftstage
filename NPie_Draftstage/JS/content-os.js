    /**
     * @file 哌稿场 · 档期 (NPie Draftstage)
     * @description 单文件原生 JS 实现，含倒排日历与选题卡联动
     */

    const MS_DAY = 86400000;
    const TODAY = (() => { const d = new Date(); d.setHours(0,0,0,0); return d; })();
    const YEAR = TODAY.getFullYear();
    const DEFAULT_START = new Date(YEAR, 6, 1);
    const DEFAULT_END = new Date(YEAR, 11, 31);

    // ── 2026 年中国法定节假日（日期字符串 Set）────────────────
    const HOLIDAYS = new Set([
      '2026-01-01', // 元旦
      '2026-02-17','2026-02-18','2026-02-19','2026-02-20','2026-02-21','2026-02-22','2026-02-23', // 春节
      '2026-04-05', // 清明
      '2026-05-01','2026-05-02','2026-05-03','2026-05-04','2026-05-05', // 劳动节
      '2026-06-19', // 端午
      '2026-09-25', // 中秋
      '2026-10-01','2026-10-02','2026-10-03','2026-10-04','2026-10-05','2026-10-06','2026-10-07', // 国庆
    ]);

    /** 是否为工作日（非周末、非法定假日） */
    function isBusinessDay(d) {
      const day = d.getDay();
      if (day === 0 || day === 6) return false;
      if (HOLIDAYS.has(fmt(d))) return false;
      return true;
    }

    /** 往前找最近的一个工作日（不含 date 本身） */
    function prevBusinessDay(date) {
      const d = new Date(date);
      d.setDate(d.getDate() - 1);
      while (!isBusinessDay(d)) d.setDate(d.getDate() - 1);
      return d;
    }

    /** 往前减 n 个工作日，返回结果日期 */
    function subtractBusinessDays(date, n) {
      const d = new Date(date);
      let count = 0;
      while (count < n) {
        d.setDate(d.getDate() - 1);
        if (isBusinessDay(d)) count++;
      }
      return d;
    }

    /** @type {Record<string, Array<{id:string,name:string,days:number,color:string,desc?:string}>>} */
    const WORKFLOWS = {
      self: [
        { id: 'prep',    name: '前置准备',   days: 1, color: '#B08A53' },
        { id: 'script',  name: '脚本',       days: 1, color: '#A46858' },
        { id: 'a_roll',  name: 'A-roll',     days: 1, color: '#8B9B7A' },
        { id: 'b_roll',  name: 'B-roll',     days: 1, color: '#7C8E99' },
        { id: 'edit',    name: '剪辑',       days: 2, color: '#C6A25C' },
        { id: 'package', name: '包装',       days: 1, color: '#B5A890' },
        { id: 'cover',   name: '封面',       days: 1, color: '#C8B8A0' },
        { id: 'copy',    name: '文案',       days: 1, color: '#D4C0B0' },
        { id: 'publish', name: '发布',       days: 1, color: '#A09080' },
      ],
      commercial: [
        { id: 'brief',   name: '收到并拆解 Brief', days: 2, color: '#C8A080' },
        { id: 'outline', name: '完成脚本大纲',     days: 3, color: '#B89870' },
        { id: 'review',  name: '品牌审核',         days: 2, color: '#9B8AA5' },
        { id: 'script',  name: '脚本',             days: 1, color: '#A46858' },
        { id: 'a_roll',  name: 'A-roll',           days: 1, color: '#8B9B7A' },
        { id: 'b_roll',  name: 'B-roll',           days: 1, color: '#7C8E99' },
        { id: 'edit',    name: '剪辑',             days: 2, color: '#C6A25C' },
        { id: 'package', name: '包装',             days: 1, color: '#B5A890' },
        { id: 'cover',   name: '封面',             days: 1, color: '#C8B8A0' },
        { id: 'copy',    name: '文案',             days: 1, color: '#D4C0B0' },
        { id: 'publish', name: '发布',             days: 1, color: '#A09080' },
      ]
    };

    /** @type {{topics: Topic[], selectedTopicId: string|null, viewStart: Date, viewEnd: Date, activeNav: string, drag: object|null}} */
    const state = {
      topics: [],
      selectedTopicId: null,
      viewStart: DEFAULT_START,
      viewEnd: DEFAULT_END,
      activeNav: 'topics',
      drag: null,
      sidebarCollapsed: false
    };

    /**
     * @typedef {{text: string, completed: boolean}} PrepItem
     * @typedef {{id: string, name: string, days: number, color: string, startDate: string, endDate: string, completed: boolean}} Task
     * @typedef {{id: string, title: string, publishDate: string, type: 'self'|'commercial', prep: PrepItem[], tasks: Task[], archived: boolean, obsidianUrl: string, status: string, priority: number, budget: string}} Topic
     */

    /** @returns {string} */
    function uid() { return 't' + Date.now() + Math.random().toString(36).slice(2, 6); }

    /** @param {Date} d @param {number} n @returns {Date} */
    function addDays(d, n) { const r = new Date(d); r.setDate(r.getDate() + n); return r; }

    /** @param {Date} d @returns {string} 本地日期 YYYY-MM-DD，不用 UTC */
    function fmt(d) {
      return d.getFullYear() + '-' +
        String(d.getMonth() + 1).padStart(2, '0') + '-' +
        String(d.getDate()).padStart(2, '0');
    }

    /** @param {string} s @returns {Date} */
    function parse(s) { return new Date(s + 'T00:00:00'); }

    /** @param {string} s @returns {string} */
    function esc(s) {
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    /** 颜色数组 */
    const TOPIC_COLORS = [
      { main: '#B08A53', bg: '#F5EFE6' },
      { main: '#A46858', bg: '#F3EAE7' },
      { main: '#8B9B7A', bg: '#E7ECE4' },
      { main: '#7C8E99', bg: '#E5E9EC' },
      { main: '#C6A25C', bg: '#F8F3E7' },
      { main: '#9B8AA5', bg: '#ECE8EF' },
      { main: '#6B8E8F', bg: '#E3EAEA' },
      { main: '#D4A373', bg: '#F8F1E8' }
    ];

    /** 获取选题颜色 */
    function getTopicColor(index) {
      return TOPIC_COLORS[index % TOPIC_COLORS.length];
    }

    /** 格式化日期为 M/D 格式 */
    function fmtShortDate(dateStr) {
      const d = parse(dateStr);
      return `${d.getMonth() + 1}/${d.getDate()}`;
    }

    /**
     * 按工作日倒排：从发布日期往前推算所有阶段日期
     * 封面/文案/发布固定在发布日当天（堆叠），其余阶段连续排在之前的营业日
     * @param {Topic} topic
     * @returns {Task[]}
     */
    function buildWorkflow(topic) {
      const wf = getWorkflowById(topic.type) || WORKFLOWS.self;
      const publishDate = topic.publishDate;
      // 先统一算所有非堆叠阶段的日期
      const nonStack = wf.filter(s => !['cover', 'copy', 'publish'].includes(s.id));
      const dateCache = {};
      let cursor = parse(publishDate);
      // 从后往前倒排
      for (let i = nonStack.length - 1; i >= 0; i--) {
        const stage = nonStack[i];
        const end = prevBusinessDay(cursor);
        const start = subtractBusinessDays(new Date(end), stage.days - 1);
        dateCache[stage.id] = { startDate: fmt(start), endDate: fmt(end) };
        cursor = new Date(start);
      }

      return wf.map(stage => {
        const existing = (topic.tasks || []).find(t => t.id === stage.id);
        if (['cover', 'copy', 'publish'].includes(stage.id)) {
          return {
            id: stage.id, name: stage.name, days: stage.days, color: stage.color,
            completed: existing ? existing.completed : false,
            startDate: publishDate, endDate: publishDate
          };
        }
        return {
          id: stage.id, name: stage.name, days: stage.days, color: stage.color,
          completed: existing ? existing.completed : false,
          ...dateCache[stage.id]
        };
      });
    }

    /** @param {Topic} topic @returns {number} */
    function calcProgress(topic) {
      const total = topic.prep.length + topic.tasks.length;
      if (!total) return 0;
      const done = topic.prep.filter(p => p.completed).length + topic.tasks.filter(t => t.completed).length;
      return Math.round((done / total) * 100);
    }

    /**
     * 跑马灯筛选规则（多维度）：
     *   状态=紧急          → 始终显示
     *   状态=重要 + ≤7天   → 显示
     *   影响力4-5星 + ≤7天 → 显示
     *   商单有金额 + ≤7天  → 显示
     *   自制≤3天 / 商单≤5天 → 显示（基础规则）
     */
    function isTopicUrgent(topic) {
      if (topic.archived || calcProgress(topic) >= 100) return false;
      const today = new Date(); today.setHours(0,0,0,0);
      const days = Math.round((parse(topic.publishDate) - today) / MS_DAY);
      // 紧急标记：无视天数
      if (topic.status === 'urgent') return true;
      // 重要 / 高影响力 / 商单有金额：宽限至 7 天
      const highPriority = (topic.status === 'important') || (topic.priority >= 4) || (!!topic.budget && topic.type === 'commercial');
      if (highPriority && days <= 7) return true;
      // 基础规则
      const limit = topic.type === 'commercial' ? 5 : 3;
      return days <= limit;
    }

    /** 跑马灯排序权重（越大越靠前） */
    function tickerWeight(topic) {
      let w = 0;
      const today = new Date(); today.setHours(0,0,0,0);
      const days = Math.round((parse(topic.publishDate) - today) / MS_DAY);
      // 状态
      if (topic.status === 'urgent') w += 200;
      else if (topic.status === 'important') w += 80;
      // 影响力
      w += (topic.priority || 0) * 15;
      // 商单金额（有金额+40，金额含数字可以按量级加）
      if (topic.budget && topic.type === 'commercial') {
        w += 40;
        const nums = topic.budget.match(/[\d.]+/g);
        if (nums) {
          const val = parseFloat(nums.join(''));
          if (val >= 100000) w += 30;
          else if (val >= 10000) w += 15;
        }
      }
      // 临近度（越近权重越高）
      w += Math.max(0, 50 - days * 5);
      return w;
    }

    /** 规范化前置准备数据结构 */
    function normalizePrep(prep) {
      if (!Array.isArray(prep)) return [];
      return prep.map(p => typeof p === 'string' ? { text: p, completed: false } : { text: p.text || '', completed: !!p.completed });
    }

    /** 初始化模拟数据 */
    function seedData() {
      const base = addDays(TODAY, 14);
      state.topics = [
        {
          id: 't1', title: 'DJI Mic Mini 2s', type: 'self',
          publishDate: fmt(addDays(base, 0)),
          prep: [
            { text: '产品功能研究与竞品对比', completed: true },
            { text: '收集官方素材与参数', completed: false }
          ],
          tasks: []
        },
        {
          id: 't2', title: '夏日充电器横评', type: 'commercial',
          publishDate: fmt(addDays(base, 7)),
          prep: [
            { text: '客户 Brief 确认', completed: true },
            { text: '品牌审核节点预留', completed: false }
          ],
          tasks: []
        },
        {
          id: 't3', title: '用 AI 做 BGM 教程', type: 'self',
          publishDate: fmt(addDays(base, 14)),
          prep: [{ text: '音乐风格探索与工具调研', completed: false }],
          tasks: []
        },
        {
          id: 't4', title: 'WAIC 大会现场报道', type: 'commercial',
          publishDate: fmt(addDays(base, 21)),
          prep: [
            { text: '展会日程与采访名单', completed: false },
            { text: '媒体证件与设备清单', completed: false }
          ],
          tasks: []
        },
        {
          id: 't5', title: '桌面收纳好物分享', type: 'self',
          publishDate: fmt(addDays(base, 28)),
          prep: [{ text: '选品清单整理', completed: false }],
          tasks: []
        },
        {
          id: 't6', title: '智能手表续航实测', type: 'self',
          publishDate: fmt(addDays(base, 35)),
          prep: [{ text: '测试方案设计', completed: false }],
          tasks: []
        }
      ];
      state.topics.forEach(t => {
        t.archived = false;
        t.obsidianUrl = t.obsidianUrl || '';
        t.status = t.status || 'normal';
        t.priority = t.priority || 0;
        t.budget = t.budget || '';
        t.prep = normalizePrep(t.prep);
        t.tasks = buildWorkflow(t);
      });
    }

    /** 扩展时间轴右边界 */
    function updateBounds() {
      let maxEnd = DEFAULT_END;
      state.topics.forEach(t => {
        const pd = parse(t.publishDate);
        if (pd > maxEnd) maxEnd = pd;
        t.tasks.forEach(task => {
          const ed = parse(task.endDate);
          if (ed > maxEnd) maxEnd = ed;
        });
      });
      state.viewEnd = maxEnd;
      state.viewStart = DEFAULT_START;
    }

    /** @returns {Date[]} */
    function getDates() {
      const dates = [];
      const n = Math.round((state.viewEnd - state.viewStart) / MS_DAY) + 1;
      for (let i = 0; i < n; i++) dates.push(addDays(state.viewStart, i));
      document.documentElement.style.setProperty('--timeline-day-count', n);
      return dates;
    }

    /** @param {string} msg */
    function toast(msg) {
      const el = document.getElementById('toast');
      el.textContent = msg;
      el.classList.add('show');
      clearTimeout(el._timer);
      el._timer = setTimeout(() => el.classList.remove('show'), 2400);
    }

    /** 持久化 */
    function save() {
      try { localStorage.setItem('content-os-v2', JSON.stringify(state.topics)); } catch (_) {}
    }

    function load() {
      try {
        const raw = localStorage.getItem('content-os-v2');
        if (!raw) return false;
        const topics = JSON.parse(raw);
        if (!Array.isArray(topics) || !topics.length) return false;

        state.topics = topics.map(t => {
          const newTopic = { ...t, prep: normalizePrep(t.prep) };
          if (newTopic.archived == null) newTopic.archived = false; // 向后兼容旧数据
          if (newTopic.obsidianUrl == null) newTopic.obsidianUrl = '';
          if (newTopic.status == null) newTopic.status = 'normal';
          if (newTopic.priority == null) newTopic.priority = 0;
          if (newTopic.budget == null) newTopic.budget = '';

          // 迁移旧版 edit1/edit2 → edit（v2.0 合并）
          const hasOldEdit = t.tasks?.some(s => s.id === 'edit1' || s.id === 'edit2');
          if (hasOldEdit) {
            newTopic.tasks = buildWorkflow(newTopic);
            // 迁移完成状态：旧 edit1 或 edit2 任一完成 → 新 edit 完成
            const oldDone = t.tasks.some(s => (s.id === 'edit1' || s.id === 'edit2') && s.completed);
            if (oldDone) {
              const editTask = newTopic.tasks.find(s => s.id === 'edit');
              if (editTask) editTask.completed = true;
            }
            // 迁移其他阶段的完成状态
            t.tasks.forEach(saved => {
              if (saved.id === 'edit1' || saved.id === 'edit2') return;
              const nt = newTopic.tasks.find(s => s.id === saved.id);
              if (nt && saved.completed) nt.completed = true;
            });
          } else if (Array.isArray(t.tasks) && t.tasks.length) {
            // 已有 v2.0 格式的保存数据：保留手动调整的日期
            newTopic.tasks = buildWorkflow(newTopic);
            t.tasks.forEach(saved => {
              if (saved.id && saved.id.startsWith('custom_')) return; // 下面单独处理
              const nt = newTopic.tasks.find(s => s.id === saved.id);
              if (nt && saved.completed) nt.completed = true;
              if (nt && saved.startDate && saved.endDate) {
                // 保留手动微调的日期（如果与倒排结果不同）
                // 仅当用户手动拖过才保留；此处简化：始终用倒排结果
              }
            });
          } else {
            newTopic.tasks = buildWorkflow(newTopic);
          }
          // 保留自定义日程
          const customTasks = (t.tasks || []).filter(s => s.id && s.id.startsWith('custom_'));
          newTopic.tasks = newTopic.tasks.concat(customTasks);

          return newTopic;
        });
        return true;
      } catch (_) { return false; }
    }

    /** 根据当前视图返回可见选题 */
    function visibleTopics() {
      if (state.activeNav === 'archived') return state.topics.filter(t => t.archived);
      return state.topics.filter(t => !t.archived);
    }

    /** 渲染侧边栏 */
    function renderSidebar() {
      const topics = visibleTopics();
      const isArchivedView = state.activeNav === 'archived';
      document.getElementById('sidebar').innerHTML = `
        <div class="sidebar-top">
          <button class="sidebar-toggle" id="sidebar-toggle" title="${state.sidebarCollapsed ? '展开侧栏' : '收起侧栏'}">${state.sidebarCollapsed ? '▶' : '◀'}</button>
          <div class="brand-row">
            <img class="brand-logo" src="IMG/NPIEAI_logo.jpg" alt="" />
            <div class="brand-text">
              <div class="brand-title">NPie Draftstage</div>
              <div class="brand-subtitle">哌稿场 · 档期</div>
            </div>
          </div>
        </div>

        <nav class="nav-list">
          <button class="nav-pill ${state.activeNav === 'timeline' ? 'active' : ''}" data-nav="timeline">排期日历</button>
          <button class="nav-pill ${state.activeNav === 'topics' ? 'active' : ''}" data-nav="topics">选题卡</button>
          <button class="nav-pill ${state.activeNav === 'archived' ? 'active' : ''}" data-nav="archived">已存档</button>
        </nav>

        <div class="sidebar-divider"></div>
        <div class="sidebar-section-label">${isArchivedView ? '已存档选题' : '选题目录'}</div>

        <div class="topic-list" id="sidebar-topic-list">
          ${topics.length === 0
            ? `<div style="padding:12px 14px;color:var(--text-muted);font-size:0.76rem;">${isArchivedView ? '暂无已存档选题' : '暂无选题'}</div>`
            : topics.map((topic, index) => {
            const sel = state.selectedTopicId === topic.id;
            const urgent = isTopicUrgent(topic);
            const colorObj = getTopicColor(index);
            return `
              <div class="topic-item ${sel ? 'selected' : ''} ${urgent ? 'topic-urgent' : ''}" data-sidebar-topic="${topic.id}"
                   style="border-left-color: ${colorObj.main}; background-color: ${colorObj.bg};">
                <span class="topic-item-badge badge-${topic.type}">${topic.type === 'self' ? '自' : '商'}</span>
                <span class="topic-item-title">${esc(topic.title)}</span>
              </div>
            `;
          }).join('')}
        </div>

        <!-- 第一部分：导出/导入 + 说明 -->
        <div class="sidebar-bottom">
          <div class="sidebar-bottom-btns">
            <button class="tool-btn" id="btn-export" title="导出备份"><img src="IMG/Export.svg" alt="" class="tool-btn-icon" /><span class="tool-btn-text">导出备份</span></button>
            <button class="tool-btn" id="btn-import" title="导入恢复"><img src="IMG/Import.svg" alt="" class="tool-btn-icon" /><span class="tool-btn-text">导入恢复</span></button>
          </div>
          <div class="sidebar-bottom-text">
            <p style="margin:0;font-size:0.56rem;line-height:1.5;">导出 — 将全部选题数据保存为 JSON 文件；导入 — 从备份文件恢复选题数据。</p>
          </div>
        </div>
        <!-- 第二部分：关于/设置 + slogan -->
        <div class="sidebar-footer">
          <div class="sidebar-links">
            <button class="sidebar-link" id="btn-about" title="关于嗯哌">
              <img src="IMG/About.svg" alt="" class="sidebar-link-icon" /><span>关于嗯哌</span>
            </button>
            <button class="sidebar-link" id="btn-settings" title="设置">
              <img src="IMG/Settings.svg" alt="" class="sidebar-link-icon" /><span>设置</span>
            </button>
          </div>
          <p class="sidebar-slogan">
            <span>NPie Draftstage – Creator Content Schedule</span>
            <span>哌稿场——创作者内容排期看板</span>
          </p>
        </div>
      `;

      // 侧边栏折叠切换
      const sidebarEl = document.getElementById('sidebar');
      if (state.sidebarCollapsed) sidebarEl.classList.add('collapsed');
      const toggleBtn = document.getElementById('sidebar-toggle');
      if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
          state.sidebarCollapsed = !state.sidebarCollapsed;
          sidebarEl.classList.toggle('collapsed', state.sidebarCollapsed);
          toggleBtn.textContent = state.sidebarCollapsed ? '▶' : '◀';
          toggleBtn.title = state.sidebarCollapsed ? '展开侧栏' : '收起侧栏';
        });
      }

      // 绑定导航事件
      document.querySelectorAll('[data-nav]').forEach(btn => {
        btn.addEventListener('click', () => {
          state.activeNav = btn.dataset.nav;
          state.selectedTopicId = null;
          render();
          // 先 render 更新 DOM（显隐排期区域会影响选题卡位置），再滚动
          requestAnimationFrame(() => {
            if (state.activeNav === 'timeline') {
              document.getElementById('timeline-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
              document.getElementById('topics-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          });
        });
      });

      // 绑定侧边栏选题点击事件
      document.querySelectorAll('[data-sidebar-topic]').forEach(item => {
        item.addEventListener('click', () => {
          state.selectedTopicId = item.dataset.sidebarTopic;
          state.activeNav = 'topics';
          render();
          // 等待渲染完成后滚动到对应选题卡
          setTimeout(() => {
            const cardEl = document.querySelector(`[data-card-id="${item.dataset.sidebarTopic}"]`);
            if (cardEl) {
              cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
              // 高亮效果
              cardEl.style.transition = 'box-shadow 0.3s ease';
              cardEl.style.boxShadow = '0 0 0 3px rgba(176, 138, 83, 0.4)';
              setTimeout(() => {
                cardEl.style.boxShadow = '';
              }, 1500);
            } else {
              document.getElementById('topics-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }, 50);
        });
      });

      document.getElementById('btn-export').onclick = () => {
        const blob = new Blob([JSON.stringify({ topics: state.topics }, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `content-os-${fmt(new Date())}.json`;
        a.click();
        toast('已导出备份');
      };
      document.getElementById('btn-import').onclick = () => document.getElementById('import-file').click();
      document.getElementById('btn-about').onclick = () => {}; // 预留
      document.getElementById('btn-settings').onclick = () => openSettingsModal();
    }

    /**
     * 用 canvas 测量文字宽度（字体与任务块一致：600 0.65rem Poppins/PingFang SC）
     * @param {string} text
     * @returns {number} px
     */
    const _measureCanvas = document.createElement('canvas');
    const _measureCtx    = _measureCanvas.getContext('2d');
    function measureText(text) {
      _measureCtx.font = '600 10.88px "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif';
      return _measureCtx.measureText(text).width;
    }

    /**
     * 根据所有选题任务名称，计算合适的单列宽度
     * 最小 58px（约 4 个汉字），最大 120px
     * @returns {number}
     */
    function calcCellWidth() {
      const MIN_CELL = 58;
      const MAX_CELL = 150;
      const PAD = 20; // 左右 padding + border 余量
      let best = MIN_CELL;

      visibleTopics().forEach(topic => {
        topic.tasks.forEach(task => {
          const start = parse(task.startDate);
          const end   = parse(task.endDate);
          const span  = Math.max(1, Math.round((end - start) / MS_DAY) + 1);
          const w     = measureText(task.name);
          // 每天需要的宽度 = (文字宽 + padding) / 跨天数，向上取整
          const perDay = Math.ceil((w + PAD) / span);
          if (perDay > best) best = perDay;
        });
      });

      return Math.min(best, MAX_CELL);
    }

    /**
     * 渲染排期日历
     */
    function renderTimeline() {
      updateBounds();
      const dates = getDates();
      const todayStr = fmt(TODAY);
      const CELL = calcCellWidth();

      /** 月份分组 */
      const months = [];
      dates.forEach(d => {
        const key = `${d.getFullYear()}-${d.getMonth()}`;
        const last = months[months.length - 1];
        if (!last || last.key !== key) months.push({ key, label: `${d.getMonth() + 1}月`, span: 1 });
        else last.span++;
      });

      let monthHtml = '<div class="month-corner"></div>';
      months.forEach(m => {
        monthHtml += `<div class="month-label-cell" style="width:${m.span * CELL}px;min-width:${m.span * CELL}px">${m.label}</div>`;
      });

      let headerHtml = '<div class="timeline-corner">选题</div>';
      dates.forEach((d, i) => {
        const isToday = fmt(d) === todayStr;
        const isFirst = i === 0 || d.getDate() === 1;
        const cls = [d.getDay() === 0 || d.getDay() === 6 ? 'weekend' : '', isToday ? 'today' : ''].filter(Boolean).join(' ');
        headerHtml += `<div class="day-cell ${cls}" style="width:${CELL}px;min-width:${CELL}px">
          ${isFirst ? `<span class="day-month-label">${d.getMonth()+1}月</span>` : ''}
          <span class="day-date">${d.getDate()}</span>
          <span class="day-week">${'日一二三四五六'[d.getDay()]}</span>
          ${isToday ? '<span class="day-today-label">今天</span>' : ''}
        </div>`;
      });

      let rowsHtml = '';
      visibleTopics().forEach((topic, index) => {
        const sel = state.selectedTopicId === topic.id;
        const urgent = isTopicUrgent(topic);
        const colorObj = getTopicColor(index);
        const progress = calcProgress(topic);
        rowsHtml += `<div class="timeline-row" data-row-id="${topic.id}">`;
        rowsHtml += `<div class="topic-label ${sel ? 'selected' : ''} ${urgent ? 'tl-urgent' : ''}" draggable="true" data-label-id="${topic.id}">
          <div class="topic-label-card" style="border-left-color: ${urgent ? '#E08840' : colorObj.main}; background-color: ${colorObj.bg}; position: relative;">
            ${urgent ? '<span class="tl-urgent-dot" title="紧急选题">急</span>' : ''}
            <span class="tl-type-dot dot-${topic.type}">${topic.type === 'self' ? '自' : '商'}</span>
            <div class="topic-label-name" data-rename-label="${topic.id}" title="${esc(topic.title)}">${esc(topic.title)}</div>
            <div class="topic-label-meta">
              <span class="topic-label-date">${fmtShortDate(topic.publishDate)}</span>
              <span style="color:var(--border)">·</span>
              <span class="topic-label-progress">${progress}%</span>
            </div>
          </div>
          <img class="topic-label-arrow ${topic.obsidianUrl ? 'has-url' : ''}" src="IMG/Obsidian.webp" alt="" title="${topic.obsidianUrl ? '打开 Obsidian 笔记' : '设置 Obsidian 链接'}" data-obsidian-label="${topic.id}" />
        </div>`;
        rowsHtml += `<div class="track-area" data-track-id="${topic.id}">`;
        dates.forEach(d => {
          const ds = fmt(d);
          const cls = [ds === todayStr ? 'today' : '', d.getDay() === 0 || d.getDay() === 6 ? 'weekend' : ''].filter(Boolean).join(' ');
          rowsHtml += `<div class="track-cell ${cls}" style="width:${CELL}px;min-width:${CELL}px" data-date="${ds}" data-track="${topic.id}"></div>`;
        });
        // ── 重叠检测：同一日期的任务按可用空间自适应尺寸 + 上下错开 ──
        const allTasks = topic.tasks;
        const groupsByRange = new Map();
        allTasks.forEach(task => {
          const key = task.startDate + '|' + task.endDate;
          if (!groupsByRange.has(key)) groupsByRange.set(key, []);
          groupsByRange.get(key).push(task);
        });
        // stackInfo: taskId → 完整行内样式字符串（top + 必要时缩小尺寸）
        const stackInfo = new Map();
        const ROW_H = 90;
        groupsByRange.forEach(group => {
          const n = group.length;
          if (n < 2) return;
          // 根据任务数反算每个块能占的高度
          const minGap = n >= 3 ? 2 : 5;
          const avail = ROW_H - (n + 1) * minGap;
          const blockH = Math.floor(avail / n);
          // n≥3 时缩小 min-height + padding 让文字不溢出
          const compact = n >= 3;
          const padV = compact ? 2 : 4;
          const padH = compact ? 5 : 8;
          const minH  = Math.max(14, blockH - 2 - padV * 2); // 减去 border + padding
          group.forEach((task, i) => {
            const top = minGap + i * (blockH + minGap);
            const sizePart = compact
              ? `min-height:${minH}px;padding:${padV}px ${padH}px;`
              : '';
            stackInfo.set(task.id, `top:${top}px;transform:none;${sizePart}`);
          });
        });

        allTasks.forEach(task => {
          const si = dates.findIndex(d => fmt(d) === task.startDate);
          const ei = dates.findIndex(d => fmt(d) === task.endDate);
          if (si < 0 || ei < 0) return;
          const left  = si * CELL + 2;
          const width = (ei - si + 1) * CELL - 4;

          const posStyle = stackInfo.get(task.id) || '';
          // 无行内样式 → CSS top:50%;transform:translateY(-50%) 居中 + 基础尺寸

          const stageClass = task.id.startsWith('custom_') ? 'stage-custom' : `stage-${task.id}`;
          rowsHtml += `<div class="task-block ${stageClass} ${task.completed ? 'completed' : ''}"
            draggable="true" data-task-topic="${topic.id}" data-task-id="${esc(task.id)}"
            style="left:${left}px;width:${width}px;${posStyle}">
            <div class="task-block-name">${esc(task.name)}</div>
          </div>`;
        });
        rowsHtml += '</div></div>';
      });

      document.getElementById('timeline-inner').innerHTML =
        `<div class="timeline-header-row">${headerHtml}</div>` +
        rowsHtml;

      bindTimelineEvents(dates, CELL);
    }

    /**
     * 绑定日历区交互事件
     * @param {Date[]} dates
     * @param {number} cellW
     */
    function bindTimelineEvents(dates, cellW) {
      const inner = document.getElementById('timeline-inner');

      /** 选题标签：选中 / 整条移动 / 顺序调整 */
      inner.querySelectorAll('.topic-label').forEach(label => {
        const topicId = label.dataset.labelId;

        label.addEventListener('click', e => {
          if (state.drag?.moved) return;
          // 点击名称文字区域 → 重命名
          if (e.target.dataset.renameLabel) {
            e.stopPropagation();
            openRenameModal(e.target.dataset.renameLabel);
            return;
          }
          state.selectedTopicId = topicId;
          render();
        });

        label.addEventListener('dragstart', e => {
          e.dataTransfer.setData('application/x-topic-move', topicId);
          e.dataTransfer.setData('application/x-topic-reorder', topicId);
          e.dataTransfer.effectAllowed = 'move';
          label.classList.add('dragging');
          state.drag = { type: 'topic', id: topicId, moved: false };
        });

        label.addEventListener('dragend', () => {
          label.classList.remove('dragging');
          state.drag = null;
        });

        label.addEventListener('dragover', e => {
          e.preventDefault();
          e.dataTransfer.dropEffect = 'move';
        });

        label.addEventListener('drop', e => {
          e.preventDefault();
          const srcId = e.dataTransfer.getData('application/x-topic-reorder');
          const tgtId = label.dataset.labelId;
          if (srcId && tgtId && srcId !== tgtId) reorderTopics(srcId, tgtId);
        });

        /** 触屏：点击选中 */
        label.addEventListener('touchend', e => {
          e.preventDefault();
          state.selectedTopicId = topicId;
          render();
          toast('已选中');
        });
      });

      /** 轨道格：整条排期落点 / 触屏落点 / 右键菜单 */
      inner.querySelectorAll('.track-cell').forEach(cell => {
        cell.addEventListener('dragover', e => {
          e.preventDefault();
          cell.classList.add('drop-target');
        });
        cell.addEventListener('dragleave', () => cell.classList.remove('drop-target'));
        cell.addEventListener('drop', e => {
          e.preventDefault();
          cell.classList.remove('drop-target');
          // 拖拽落点后清除选中态，利用 click 处理器已有的 selectedTopicId 守卫防止误触整条排期移动
          state.selectedTopicId = null;
          const taskPayload = e.dataTransfer.getData('application/x-task-move');
          if (taskPayload) {
            const { topicId, taskId } = JSON.parse(taskPayload);
            moveSingleTask(topicId, taskId, cell.dataset.date);
            return;
          }
          const topicId = e.dataTransfer.getData('application/x-topic-move');
          if (topicId) {
            moveWholeSchedule(topicId, cell.dataset.date);
            if (state.drag) state.drag.moved = true;
          }
        });
        // 右键菜单 — 空格子新增日程，有任务的格子显示删除
        cell.addEventListener('click', e => {
          // 显式阻止 cell 上的任何点击行为，移动排期仅通过拖拽完成
          e.preventDefault();
          e.stopPropagation();
        });
        cell.addEventListener('contextmenu', e => {
          e.preventDefault();
          const topicId = cell.dataset.track;
          const date    = cell.dataset.date;
          const topic   = state.topics.find(t => t.id === topicId);
          if (!topic) return;
          // 筛选该日期上有哪些任务
          const tasksHere = topic.tasks.filter(t => t.startDate <= date && t.endDate >= date);
          if (tasksHere.length === 0) {
            // 空格子 → 新增日程
            showEmptyCellMenu(cell, topicId, date);
          } else {
            // 有任务 → 显示删除菜单
            showOccupiedCellMenu(cell, topicId, tasksHere);
          }
        });
      });

      /** 任务块：单块微调 + 自定义日程交互 */
      inner.querySelectorAll('.task-block').forEach(block => {
        const taskId  = block.dataset.taskId;
        const topicId = block.dataset.taskTopic;
        const isCustom = taskId && taskId.startsWith('custom_');

        block.addEventListener('dragstart', e => {
          e.stopPropagation();
          const payload = { topicId, taskId };
          e.dataTransfer.setData('application/x-task-move', JSON.stringify(payload));
          e.dataTransfer.effectAllowed = 'move';
        });

        // 单击：阻止冒泡
        block.addEventListener('click', e => e.stopPropagation());

        // 双击：重命名（所有节点通用）
        block.addEventListener('dblclick', e => {
          e.stopPropagation();
          e.preventDefault();
          openTaskRename(topicId, taskId);
        });

        // 右键：删除节点
        block.addEventListener('contextmenu', e => {
          e.preventDefault();
          e.stopPropagation();
          showTaskContextMenu(e.currentTarget, topicId, taskId);
        });
      });

      /** 日历选题标签 Obsidian 图标点击 */
      inner.querySelectorAll('[data-obsidian-label]').forEach(icon => {
        icon.addEventListener('click', e => {
          e.stopPropagation();
          const topic = state.topics.find(t => t.id === icon.dataset.obsidianLabel);
          if (!topic) return;
          if (topic.obsidianUrl) {
            window.location.href = topic.obsidianUrl;
          } else {
            openObsidianModal(topic.id);
          }
        });
      });

      /** 鼠标拖拽整条排期（增强体验） */
      inner.querySelectorAll('.topic-label').forEach(label => {
        let dragging = false;
        let topicId = label.dataset.labelId;

        label.addEventListener('mousedown', e => {
          if (e.button !== 0) return;
          dragging = true;
          topicId = label.dataset.labelId;
          state.selectedTopicId = topicId;
        });

        document.addEventListener('mouseup', () => { dragging = false; });

        label.addEventListener('mouseenter', () => {
          if (!dragging) return;
          const row = label.closest('.timeline-row');
          if (row) row.style.background = 'rgba(176,138,83,0.04)';
        });
        label.addEventListener('mouseleave', () => {
          const row = label.closest('.timeline-row');
          if (row) row.style.background = '';
        });
      });
    }

    /**
     * 整条排期移至新发布日 — 重新按工作日倒排，保留已完成状态和自定义日程
     */
    function moveWholeSchedule(topicId, newPublishDate) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic || !newPublishDate) return;
      if (topic.publishDate === newPublishDate) return;

      // 保留完成状态
      const completedMap = new Map();
      topic.tasks.forEach(t => { if (t.completed) completedMap.set(t.id, true); });
      // 保留自定义日程
      const customTasks = topic.tasks.filter(t => t.id && t.id.startsWith('custom_'));

      topic.publishDate = newPublishDate;
      topic.tasks = buildWorkflow(topic);
      // 恢复完成状态
      topic.tasks.forEach(t => { if (completedMap.has(t.id)) t.completed = true; });
      // 追加自定义日程
      topic.tasks = topic.tasks.concat(customTasks);

      save();
      render();
      toast(`「${topic.title}」发布日 → ${newPublishDate}`);
    }

    /**
     * 微调单个任务块日期
     * @param {string} topicId
     * @param {string} taskId
     * @param {string} newStart
     */
    function moveSingleTask(topicId, taskId, newStart) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic || !newStart) return;
      // 校验目标日期有效
      if (isNaN(parse(newStart).getTime())) return;

      if (taskId === 'publish') {
        topic.publishDate = newStart;
        ['cover', 'copy', 'publish'].forEach(id => {
          const t = topic.tasks.find(t => t.id === id);
          if (t) { t.startDate = newStart; t.endDate = newStart; }
        });
      } else if (['cover', 'copy'].includes(taskId)) {
        topic.publishDate = newStart;
        ['cover', 'copy', 'publish'].forEach(id => {
          const t = topic.tasks.find(t => t.id === id);
          if (t) { t.startDate = newStart; t.endDate = newStart; }
        });
      } else {
        const task = topic.tasks.find(t => t.id === taskId);
        if (!task) return;
        // 防非法日期导致 duration 为 NaN
        const startMs = parse(task.startDate).getTime();
        const endMs   = parse(task.endDate).getTime();
        const duration = (!isNaN(startMs) && !isNaN(endMs))
          ? Math.round((endMs - startMs) / MS_DAY)
          : 0;
        task.startDate = newStart;
        task.endDate   = fmt(addDays(parse(newStart), Math.max(0, duration)));
      }

      save();
      render();
      toast(`已调整「${topic.title}」节点日期`);
    }

    /** ── 流程节点重命名与删除（统一：标准 + 自定义） ────────────────────────── */

    /**
     * 双击重命名 — 查找 DOM 中的任务块，原地 contentEditable 编辑
     */
    function openTaskRename(topicId, taskId) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      const task = topic.tasks.find(t => t.id === taskId);
      if (!task) return;

      // 在 DOM 中找对应的任务块
      const blockEl = document.querySelector(`.task-block[data-task-topic="${topicId}"][data-task-id="${CSS.escape(taskId)}"]`);
      if (!blockEl) return;
      const nameDiv = blockEl.querySelector('.task-block-name');
      if (!nameDiv) return;

      const oldName = task.name;
      nameDiv.contentEditable = 'true';
      nameDiv.focus();
      document.execCommand('selectAll', false, null);

      const commitRename = () => {
        nameDiv.contentEditable = 'false';
        const newName = nameDiv.textContent.trim();
        if (newName && newName !== oldName) {
          task.name = newName;
          save();
          render();
          toast(`已重命名为「${newName}」`);
        } else {
          nameDiv.textContent = oldName;
        }
      };

      const cancel = () => {
        nameDiv.contentEditable = 'false';
        nameDiv.textContent = oldName;
      };

      nameDiv.addEventListener('blur', commitRename, { once: true });
      nameDiv.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); nameDiv.blur(); }
        if (e.key === 'Escape') { e.preventDefault(); cancel(); }
      }, { once: true });
    }

    /** 右键任务块 → 删除节点 */
    function showTaskContextMenu(blockEl, topicId, taskId) {
      const menu = document.getElementById('ctx-menu');
      const topic = state.topics.find(t => t.id === topicId);
      const task = topic?.tasks.find(t => t.id === taskId);
      const taskName = task ? task.name : '日程';

      menu.innerHTML = `
        <div class="ctx-item danger" data-ctx="delete-task">删除「${esc(taskName)}」</div>
        <div class="ctx-separator"></div>
        <div class="ctx-item" data-ctx="cancel">取消</div>
      `;

      menu.style.left = '-9999px';
      menu.style.top  = '-9999px';
      menu.style.display = 'block';

      const rect = blockEl.getBoundingClientRect();
      const mw   = menu.offsetWidth  || 160;
      const mh   = menu.offsetHeight || 80;
      const vw   = window.innerWidth;
      const vh   = window.innerHeight;

      let left = rect.left;
      let top  = rect.bottom + 4;

      if (left + mw > vw) left = rect.right - mw;
      if (top  + mh > vh) top  = rect.top - mh - 4;
      left = Math.max(4, left);
      top  = Math.max(4, top);

      menu.style.left = left + 'px';
      menu.style.top  = top  + 'px';

      menu.querySelectorAll('[data-ctx]').forEach(item => {
        item.addEventListener('click', e => {
          e.stopPropagation();
          hideContextMenu();
          if (item.dataset.ctx === 'delete-task') deleteTaskNode(topicId, taskId);
        });
      });
    }

    function deleteTaskNode(topicId, taskId) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      const task = topic.tasks.find(t => t.id === taskId);
      if (!task) return;
      if (!confirm(`确认删除流程节点「${task.name}」？`)) return;
      topic.tasks = topic.tasks.filter(t => t.id !== taskId);
      save();
      render();
      toast(`已删除「${task.name}」`);
    }

    /** ── 右键菜单 ─────────────────────────────────────── */

    // 当前右键菜单上下文
    let _ctxTopicId = null;
    let _ctxDate    = null;

    /**
     * 右键菜单 — 定位到触发格子的正下方（左对齐），不超出视口
     * @param {HTMLElement} cellEl  触发右键的 .track-cell 元素
     * @param {string} topicId
     * @param {string} date
     */
    function showContextMenu(cellEl, topicId, date) {
      _ctxTopicId = topicId;
      _ctxDate    = date;

      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      const pct = calcProgress(topic);
      const isArchived = topic.archived;

      // 按进度和存档状态生成菜单项
      let actionItems = '';
      if (isArchived) {
        actionItems = `
          <div class="ctx-item" data-ctx="restore">恢复选题</div>
          <div class="ctx-separator"></div>
          <div class="ctx-item danger" data-ctx="force-delete">彻底删除</div>
        `;
      } else if (pct === 0) {
        actionItems = `
          <div class="ctx-item danger" data-ctx="abandon">放弃选题</div>
        `;
      } else if (pct === 100) {
        actionItems = `
          <div class="ctx-item" data-ctx="archive">存档</div>
        `;
      }

      // 只有从日历格子触发时（有 date）才显示"新增日程"
      const scheduleSection = date ? `
        <div class="ctx-item" data-ctx="add-schedule">＋ 新增日程</div>
        <div class="ctx-separator"></div>
      ` : '';

      const menu = document.getElementById('ctx-menu');
      menu.innerHTML = `
        ${scheduleSection}
        <div class="ctx-item" data-ctx="rename">重命名</div>
        ${actionItems ? '<div class="ctx-separator"></div>' + actionItems : ''}
        <div class="ctx-separator"></div>
        <div class="ctx-item" data-ctx="cancel">取消</div>
      `;

      menu.querySelectorAll('[data-ctx]').forEach(item => {
        item.addEventListener('click', e => {
          e.stopPropagation();
          hideContextMenu();
          const action = item.dataset.ctx;
          if (action === 'add-schedule') openScheduleModal(_ctxTopicId, _ctxDate);
          if (action === 'rename')       openRenameModal(_ctxTopicId);
          if (action === 'abandon')      deleteTopic(_ctxTopicId, 'abandon');
          if (action === 'archive')      archiveTopic(_ctxTopicId);
          if (action === 'restore')      archiveTopic(_ctxTopicId, false);
          if (action === 'force-delete') deleteTopic(_ctxTopicId, 'force');
        });
      });

      // 先隐藏渲染，下一帧再定位（避免尺寸未计算问题）
      menu.style.visibility = 'hidden';
      menu.style.left    = '0px';
      menu.style.top     = '0px';
      menu.style.display = 'block';

      requestAnimationFrame(() => {
        const rect = cellEl.getBoundingClientRect();
        const mw   = menu.offsetWidth  || 160;
        const mh   = menu.offsetHeight || 150;
        const vw   = window.innerWidth;
        const vh   = window.innerHeight;

        let left = rect.left;
        let top  = rect.bottom + 4;

        if (left + mw > vw) left = rect.right - mw;
        if (top  + mh > vh) top  = rect.top - mh - 4;
        left = Math.max(4, left);
        top  = Math.max(4, top);

        menu.style.left       = left + 'px';
        menu.style.top        = top  + 'px';
        menu.style.visibility = 'visible';
      });
    }

    function hideContextMenu() {
      const menu = document.getElementById('ctx-menu');
      if (menu) menu.style.display = 'none';
    }

    document.addEventListener('click', hideContextMenu);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') hideContextMenu(); });

    /** ── 空格子右键 → 新增日程 ────────────────────────────── */

    function showEmptyCellMenu(cellEl, topicId, date) {
      const menu = document.getElementById('ctx-menu');
      menu.innerHTML = `
        <div class="ctx-item" data-ctx="add-schedule">＋ 新增日程</div>
        <div class="ctx-separator"></div>
        <div class="ctx-item" data-ctx="cancel">取消</div>
      `;
      menu.querySelector('[data-ctx="add-schedule"]').addEventListener('click', e => {
        e.stopPropagation();
        hideContextMenu();
        openScheduleModal(topicId, date);
      });
      menu.querySelector('[data-ctx="cancel"]').addEventListener('click', e => {
        e.stopPropagation();
        hideContextMenu();
      });
      positionMenu(cellEl, menu);
    }

    /** ── 有任务的格子右键 → 删除该节点 ─────────────────────── */

    function showOccupiedCellMenu(cellEl, topicId, tasksHere) {
      const menu = document.getElementById('ctx-menu');
      const items = tasksHere.map(t =>
        `<div class="ctx-item danger" data-ctx="delete-task" data-task-id="${esc(t.id)}">删除「${esc(t.name)}」</div>`
      ).join('');
      menu.innerHTML = `
        ${items}
        <div class="ctx-separator"></div>
        <div class="ctx-item" data-ctx="cancel">取消</div>
      `;
      menu.querySelectorAll('[data-ctx="delete-task"]').forEach(item => {
        item.addEventListener('click', e => {
          e.stopPropagation();
          hideContextMenu();
          deleteTaskNode(topicId, item.dataset.taskId);
        });
      });
      menu.querySelector('[data-ctx="cancel"]').addEventListener('click', e => {
        e.stopPropagation();
        hideContextMenu();
      });
      positionMenu(cellEl, menu);
    }

    /** 复用菜单定位逻辑 */
    function positionMenu(cellEl, menu) {
      menu.style.visibility = 'hidden';
      menu.style.left = '0px';
      menu.style.top  = '0px';
      menu.style.display = 'block';
      requestAnimationFrame(() => {
        const rect = cellEl.getBoundingClientRect();
        const mw   = menu.offsetWidth  || 160;
        const mh   = menu.offsetHeight || 120;
        const vw   = window.innerWidth;
        const vh   = window.innerHeight;
        let left = rect.left;
        let top  = rect.bottom + 4;
        if (left + mw > vw) left = rect.right - mw;
        if (top  + mh > vh) top  = rect.top - mh - 4;
        left = Math.max(4, left);
        top  = Math.max(4, top);
        menu.style.left       = left + 'px';
        menu.style.top        = top  + 'px';
        menu.style.visibility = 'visible';
      });
    }

    /** ── 选题卡右键菜单（跟随鼠标坐标） ───────────────────── */

    function showTopicMenuAt(clientX, clientY, topicId) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      const pct = calcProgress(topic);
      const isArchived = topic.archived;

      let actionItems = '';
      if (isArchived) {
        actionItems = `
          <div class="ctx-item" data-ctx="restore">恢复选题</div>
          <div class="ctx-separator"></div>
          <div class="ctx-item danger" data-ctx="force-delete">彻底删除</div>
        `;
      } else if (pct === 0) {
        actionItems = `<div class="ctx-item danger" data-ctx="abandon">放弃选题</div>`;
      } else if (pct === 100) {
        actionItems = `<div class="ctx-item" data-ctx="archive">存档</div>`;
      }

      const menu = document.getElementById('ctx-menu');
      menu.innerHTML = `
        <div class="ctx-item" data-ctx="rename">重命名</div>
        ${actionItems ? '<div class="ctx-separator"></div>' + actionItems : ''}
        <div class="ctx-separator"></div>
        <div class="ctx-item" data-ctx="cancel">取消</div>
      `;

      menu.querySelectorAll('[data-ctx]').forEach(item => {
        item.addEventListener('click', e => {
          e.stopPropagation();
          hideContextMenu();
          const action = item.dataset.ctx;
          if (action === 'rename')       openRenameModal(topicId);
          if (action === 'abandon')      deleteTopic(topicId, 'abandon');
          if (action === 'archive')      archiveTopic(topicId);
          if (action === 'restore')      archiveTopic(topicId, false);
          if (action === 'force-delete') deleteTopic(topicId, 'force');
        });
      });

      positionMenuAt(clientX, clientY, menu);
    }

    function positionMenuAt(clientX, clientY, menu) {
      menu.style.visibility = 'hidden';
      menu.style.left = '0px';
      menu.style.top  = '0px';
      menu.style.display = 'block';
      requestAnimationFrame(() => {
        const mw = menu.offsetWidth  || 160;
        const mh = menu.offsetHeight || 120;
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        let left = clientX;
        let top  = clientY + 4;
        if (left + mw > vw) left = clientX - mw;
        if (top  + mh > vh) top  = clientY - mh - 4;
        left = Math.max(4, left);
        top  = Math.max(4, top);
        menu.style.left       = left + 'px';
        menu.style.top        = top  + 'px';
        menu.style.visibility = 'visible';
      });
    }

    /** ── 新增日程 ─────────────────────────────────────── */

    let _scheduleTopicId = null;
    let _scheduleDate    = null;

    function openScheduleModal(topicId, date) {
      _scheduleTopicId = topicId;
      _scheduleDate    = date;
      document.getElementById('schedule-modal-name').value = '';
      document.getElementById('schedule-modal-overlay').classList.add('open');
      setTimeout(() => document.getElementById('schedule-modal-name').focus(), 50);
    }

    function closeScheduleModal() {
      document.getElementById('schedule-modal-overlay').classList.remove('open');
    }

    function confirmSchedule() {
      const name = document.getElementById('schedule-modal-name').value.trim();
      if (!name) { toast('请填写日程名称'); return; }
      const topic = state.topics.find(t => t.id === _scheduleTopicId);
      if (!topic) return;
      const customId = 'custom_' + Date.now();
      topic.tasks.push({
        id: customId,
        name,
        days: 1,
        color: '#C4B8D4',
        completed: false,
        startDate: _scheduleDate,
        endDate:   _scheduleDate
      });
      save();
      closeScheduleModal();
      render();
      toast(`已添加日程「${name}」`);
    }

    /** ── 重命名 ─────────────────────────────────────── */

    let _renameTopicId = null;

    function openRenameModal(topicId) {
      _renameTopicId = topicId;
      const topic = state.topics.find(t => t.id === topicId);
      document.getElementById('rename-modal-input').value = topic ? topic.title : '';
      document.getElementById('rename-modal-overlay').classList.add('open');
      setTimeout(() => {
        const input = document.getElementById('rename-modal-input');
        input.focus();
        input.select();
      }, 50);
    }

    function closeRenameModal() {
      document.getElementById('rename-modal-overlay').classList.remove('open');
    }

    function confirmRename() {
      const name = document.getElementById('rename-modal-input').value.trim();
      if (!name) { toast('名称不能为空'); return; }
      const topic = state.topics.find(t => t.id === _renameTopicId);
      if (!topic) return;
      topic.title = name;
      save();
      closeRenameModal();
      render();
      toast(`已重命名为「${name}」`);
    }

    /** ── Obsidian 链接弹窗 ──────────────────────────────── */

    let _obsidianTopicId = null;

    function openObsidianModal(topicId) {
      _obsidianTopicId = topicId;
      const topic = state.topics.find(t => t.id === topicId);
      document.getElementById('obsidian-modal-input').value = topic?.obsidianUrl || '';
      // 已有链接才显示清除按钮
      document.getElementById('obsidian-modal-clear').style.display = topic?.obsidianUrl ? '' : 'none';
      document.getElementById('obsidian-modal-overlay').classList.add('open');
      setTimeout(() => document.getElementById('obsidian-modal-input').focus(), 50);
    }

    function closeObsidianModal() {
      document.getElementById('obsidian-modal-overlay').classList.remove('open');
    }

    function confirmObsidianUrl() {
      const url = document.getElementById('obsidian-modal-input').value.trim();
      const topic = state.topics.find(t => t.id === _obsidianTopicId);
      if (!topic) return;
      topic.obsidianUrl = url;
      save(); render();
      closeObsidianModal();
      toast(url ? 'Obsidian 链接已设置' : 'Obsidian 链接已清除');
    }

    /** ── 删除/放弃选题 ─────────────────────────────────────── */

    /**
     * @param {string} topicId
     * @param {string} [mode] 'abandon' | 'force'
     */
    function deleteTopic(topicId, mode) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      const msg = mode === 'abandon'
        ? `该选题尚未开始执行，确认放弃「${topic.title}」？`
        : `确定彻底删除「${topic.title}」？此操作无法撤销。`;
      if (!confirm(msg)) return;
      state.topics = state.topics.filter(t => t.id !== topicId);
      if (state.selectedTopicId === topicId) state.selectedTopicId = null;
      save();
      render();
      toast(mode === 'abandon' ? `已放弃「${topic.title}」` : `已删除「${topic.title}」`);
    }

    /**
     * 存档或恢复选题
     * @param {string} topicId
     * @param {boolean} [archive=true]
     */
    function archiveTopic(topicId, archive = true) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      if (archive) {
        if (!confirm(`该选题已完成，确认存档「${topic.title}」？`)) return;
        topic.archived = true;
        toast(`已存档「${topic.title}」`);
      } else {
        topic.archived = false;
        toast(`已恢复「${topic.title}」`);
      }
      if (state.selectedTopicId === topicId) state.selectedTopicId = null;
      save();
      render();
    }

    /** @param {string} fromId @param {string} toId */
    function reorderTopics(fromId, toId) {
      const fi = state.topics.findIndex(t => t.id === fromId);
      const ti = state.topics.findIndex(t => t.id === toId);
      if (fi < 0 || ti < 0 || fi === ti) return;
      const [item] = state.topics.splice(fi, 1);
      state.topics.splice(ti, 0, item);
      save();
      render();
      toast('已调整选题顺序');
    }

    /**
     * 不重建 DOM，只更新某个选题卡的进度条和百分比数字
     * @param {string} topicId
     */
    function patchCardProgress(topicId) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      const pct = calcProgress(topic);
      // progress fill bar
      const card = document.querySelector(`[data-card-id="${topicId}"]`);
      if (!card) return;
      const fill = card.querySelector('.card-progress-fill');
      if (fill) fill.style.width = pct + '%';
      const pctEl = card.querySelector('.card-progress-pct');
      if (pctEl) pctEl.textContent = pct + '%';
      // also update sidebar label progress if visible
      const sidebarLabel = document.querySelector(`.topic-label[data-label-id="${topicId}"] .topic-label-progress`);
      if (sidebarLabel) sidebarLabel.textContent = pct + '%';
    }

    /**
     * 不重建 DOM，只更新 timeline 行中某选题的任务块 completed 样式
     * @param {string} topicId
     */
    function patchTimelineRow(topicId) {
      const topic = state.topics.find(t => t.id === topicId);
      if (!topic) return;
      // update each task block's completed class
      document.querySelectorAll(`.task-block[data-task-topic="${topicId}"]`).forEach(block => {
        const taskId = block.dataset.taskId;
        const task = topic.tasks.find(t => t.id === taskId);
        if (task) block.classList.toggle('completed', !!task.completed);
      });
    }

    /** 渲染选题卡网格 */
    function renderCards() {
      const grid = document.getElementById('cards-grid');
      grid.innerHTML = visibleTopics().map(topic => {
        const pct = calcProgress(topic);
        const urgent = isTopicUrgent(topic);
        const sel = state.selectedTopicId === topic.id;
        return `
        <div class="topic-card type-${topic.type} ${sel ? 'selected' : ''} ${urgent ? 'is-urgent' : ''}" draggable="true" data-card-id="${topic.id}" style="position:relative;">

          <!-- 左上角类型角标 -->
          <span class="card-type-badge badge-${topic.type}" title="${topic.type === 'self' ? '自制内容' : '商单'}">${topic.type === 'self' ? '自' : '商'}</span>

          <!-- 第一部分：标题 + 进度 -->
          <div class="card-head">
            <div class="card-head-left">
              <div class="card-title">${esc(topic.title)}</div>
              <img class="card-obsidian-link ${topic.obsidianUrl ? 'has-url' : ''}" src="IMG/Obsidian.webp" alt="Obsidian" title="${topic.obsidianUrl ? '打开 Obsidian 笔记' : '设置 Obsidian 链接'}" data-obsidian-topic="${topic.id}" />
              <select class="card-type-select" data-type-select="${topic.id}">
                <option value="self" ${topic.type === 'self' ? 'selected' : ''}>自制内容</option>
                <option value="commercial" ${topic.type === 'commercial' ? 'selected' : ''}>商单</option>
              </select>
            </div>
            <div class="card-progress-wrap">
              <div class="card-progress-pct">${pct}%</div>
              <div class="card-progress-label">完成进度</div>
            </div>
          </div>
          <div class="card-progress-bar"><div class="card-progress-fill" style="width:${pct}%"></div></div>

          <!-- 第二部分：前置准备 -->
          <div class="card-section">
            <div class="card-section-title">前置准备</div>
            <div class="prep-row">
              <input class="prep-input" placeholder="添加准备项…" data-prep-in="${topic.id}" />
              <button class="prep-add-btn" data-prep-add="${topic.id}">+</button>
            </div>
            ${topic.prep.map((p, i) => `
              <div class="prep-item ${p.completed ? 'done' : ''}">
                <input type="checkbox" class="item-checkbox" data-prep-chk="${topic.id}:${i}" ${p.completed ? 'checked' : ''} />
                <span class="item-text">${esc(p.text)}</span>
                <button class="item-remove" data-prep-rm="${topic.id}:${i}">✕</button>
              </div>
            `).join('')}
          </div>

          <!-- 第三部分：制作流程（两列） -->
          <div class="card-section">
            <div class="card-section-title">制作流程 · 自动倒排</div>
            <div class="workflow-grid">
              ${topic.tasks.map(task => `
                <div class="workflow-item ${task.completed ? 'done' : ''}">
                  <input type="checkbox" class="item-checkbox" data-task-chk="${topic.id}:${task.id}" ${task.completed ? 'checked' : ''} />
                  <span class="workflow-dot" style="background:${task.color}"></span>
                  <span class="item-text">${esc(task.name)}</span>
                  <span class="item-date">${task.startDate.slice(5)}</span>
                </div>
              `).join('')}
            </div>
          </div>

        </div>`;
      }).join('');

      /** 卡片拖拽排序 */
      grid.querySelectorAll('.topic-card').forEach(card => {
        card.addEventListener('dragstart', e => {
          e.dataTransfer.setData('application/x-card-reorder', card.dataset.cardId);
          e.dataTransfer.effectAllowed = 'move';
        });
        card.addEventListener('dragover', e => { e.preventDefault(); card.classList.add('drag-over'); });
        card.addEventListener('dragleave', () => card.classList.remove('drag-over'));
        card.addEventListener('drop', e => {
          e.preventDefault();
          card.classList.remove('drag-over');
          const src = e.dataTransfer.getData('application/x-card-reorder');
          if (src && src !== card.dataset.cardId) reorderTopics(src, card.dataset.cardId);
        });
        card.addEventListener('click', (e) => {
          // 点击交互控件时不触发卡片选中/重渲染，避免与控件自身事件冲突
          if (e.target.closest('input, button, select')) return;
          state.selectedTopicId = card.dataset.cardId;
          render();
        });
        // 右键选题卡 → 弹出选题操作菜单（存档/放弃/恢复等）
        card.addEventListener('contextmenu', e => {
          e.preventDefault();
          showTopicMenuAt(e.clientX, e.clientY, card.dataset.cardId);
        });
      });

      /** Obsidian 链接图标点击 */
      grid.querySelectorAll('[data-obsidian-topic]').forEach(icon => {
        icon.addEventListener('click', e => {
          e.stopPropagation();
          const topic = state.topics.find(t => t.id === icon.dataset.obsidianTopic);
          if (!topic) return;
          if (topic.obsidianUrl) {
            window.location.href = topic.obsidianUrl;
          } else {
            openObsidianModal(topic.id);
          }
        });
      });

      /** 工作流类型切换 */
      grid.querySelectorAll('[data-type-select]').forEach(sel => {
        sel.addEventListener('change', () => {
          const topic = state.topics.find(t => t.id === sel.dataset.typeSelect);
          if (!topic) return;
          topic.type = sel.value;
          topic.tasks = buildWorkflow(topic);
          save();
          render();
          toast(`已切换为${sel.value === 'commercial' ? '商单' : '自制内容'}流程`);
        });
        sel.addEventListener('click', e => e.stopPropagation());
      });

      /** 前置准备 CRUD */
      grid.querySelectorAll('[data-prep-add]').forEach(btn => {
        btn.addEventListener('click', e => {
          e.stopPropagation();
          const id = btn.dataset.prepAdd;
          const input = document.querySelector(`[data-prep-in="${id}"]`);
          const text = input?.value.trim();
          if (!text) return;
          const topic = state.topics.find(t => t.id === id);
          topic.prep.push({ text, completed: false });
          save(); 
          render();
        });
      });

      // 添加回车键支持
      grid.querySelectorAll('[data-prep-in]').forEach(input => {
        input.addEventListener('keypress', e => {
          e.stopPropagation();
          if (e.key === 'Enter') {
            const id = input.dataset.prepIn;
            const text = input?.value.trim();
            if (!text) return;
            const topic = state.topics.find(t => t.id === id);
            topic.prep.push({ text, completed: false });
            save(); 
            render();
          }
        });
        input.addEventListener('click', e => {
          e.stopPropagation();
        });
      });
      grid.querySelectorAll('[data-prep-rm]').forEach(btn => {
        btn.addEventListener('click', e => {
          e.stopPropagation();
          const [id, idx] = btn.dataset.prepRm.split(':');
          state.topics.find(t => t.id === id)?.prep.splice(+idx, 1);
          save(); render();
        });
      });
      grid.querySelectorAll('[data-prep-chk]').forEach(chk => {
        chk.addEventListener('change', e => {
          e.stopPropagation();
          const [id, idx] = chk.dataset.prepChk.split(':');
          const topic = state.topics.find(t => t.id === id);
          if (!topic) return;
          const item = topic.prep[+idx];
          if (item) item.completed = chk.checked;
          // visual: strikethrough on the item row
          const row = chk.closest('.prep-item');
          if (row) row.classList.toggle('done', chk.checked);
          // update progress bar and pct in this card
          patchCardProgress(id);
          save();
          // sync timeline (completed class on task block)
          patchTimelineRow(id);
        });
      });

      /** 固定流程勾选 */
      grid.querySelectorAll('[data-task-chk]').forEach(chk => {
        chk.addEventListener('change', e => {
          e.stopPropagation();
          const [id, taskId] = chk.dataset.taskChk.split(':');
          const topic = state.topics.find(t => t.id === id);
          if (!topic) return;
          const task = topic.tasks.find(t => t.id === taskId);
          if (task) task.completed = chk.checked;
          // visual: strikethrough on the item row
          const row = chk.closest('.workflow-item');
          if (row) row.classList.toggle('done', chk.checked);
          // update progress bar and pct in this card
          patchCardProgress(id);
          save();
          // sync timeline task block
          patchTimelineRow(id);
        });
      });
    }

    /** 新增选题弹窗 */
    function openAddModal(defaultDate) {
      const overlay = document.getElementById('modal-overlay');
      updateTypeSelect(); // 确保工作流类型下拉最新
      document.getElementById('modal-title').value = '';
      document.getElementById('modal-type').value = 'self';
      document.getElementById('modal-date').value = defaultDate || fmt(addDays(TODAY, 14));
      document.querySelector('input[name="modal-status"][value="normal"]').checked = true;
      document.getElementById('modal-priority-val').value = '0';
      document.getElementById('modal-budget').value = '';
      document.getElementById('modal-budget-field').style.display = 'none';
      // 重置星星
      document.querySelectorAll('#modal-priority span').forEach(s => s.classList.remove('active'));
      overlay.classList.add('open');
    }

    function closeModal() {
      document.getElementById('modal-overlay').classList.remove('open');
    }

    function confirmAdd() {
      const title = document.getElementById('modal-title').value.trim();
      const type = document.getElementById('modal-type').value;
      const publishDate = document.getElementById('modal-date').value;
      if (!title || !publishDate) { toast('请填写名称与发布日期'); return; }
      const status = document.querySelector('input[name="modal-status"]:checked')?.value || 'normal';
      const priority = parseInt(document.getElementById('modal-priority-val').value) || 0;
      const budget = document.getElementById('modal-budget').value.trim();
      const topic = { id: uid(), title, type, publishDate, prep: [], tasks: [], archived: false, obsidianUrl: '', status, priority, budget };
      topic.tasks = buildWorkflow(topic);
      state.topics.push(topic);
      save();
      closeModal();
      render();
      toast(`已添加「${title}」`);
    }

    /** 更新顶部通知跑马灯 */
    function updateTicker() {
      const el = document.getElementById('header-ticker');
      if (!el) return;
      const today = new Date(); today.setHours(0,0,0,0);
      const urgent = state.topics.filter(t => isTopicUrgent(t));
      // 按权重排序
      urgent.sort((a, b) => tickerWeight(b) - tickerWeight(a));
      if (!urgent.length) {
        el.innerHTML = '<span class="header-ticker-empty">暂无紧急选题 · 一切尽在掌控</span>';
        return;
      }
      const items = urgent.map(t => {
        const days = Math.round((parse(t.publishDate) - today) / MS_DAY);
        const tag = t.type === 'commercial' ? '商单' : '自制';
        const stars = t.priority > 0 ? '★'.repeat(t.priority) : '';
        const budget = t.budget ? ` [${t.budget}]` : '';
        const statusLabel = t.status === 'urgent' ? '🚨' : (t.status === 'important' ? '📌' : '');
        let cls = '';
        if (t.status === 'urgent' || days <= 1) cls = 'urgent';
        else if (days <= 3) cls = 'urgent';
        const prefix = cls === 'urgent' ? '🔥' : '⚡';
        return { text: `${statusLabel}${prefix} ${tag} · ${t.title}${stars}${budget} — ${days}天后发布`, cls };
      });
      const source = items.length >= 3 ? items : [...items, ...items];
      const doubled = [...source, ...source];
      el.innerHTML = `<div class="header-ticker-track">${doubled.map(i =>
        `<span class="header-ticker-item ${i.cls}">${esc(i.text)}</span>`
      ).join(' &nbsp;·&nbsp; ')}</div>`;
    }

    /** 全局渲染 */
    function render() {
      // 视图相关 UI 控制
      const isArchived = state.activeNav === 'archived';
      const addBtn = document.getElementById('btn-add-topic');
      if (addBtn) addBtn.style.display = isArchived ? 'none' : '';
      const timelineSection = document.getElementById('timeline-section');
      if (timelineSection) timelineSection.style.display = isArchived ? 'none' : '';
      const topicsTitle = document.querySelector('.topics-title-large');
      if (topicsTitle) topicsTitle.textContent = isArchived ? '已存档选题' : '选题卡';
      const topicsSubtitle = document.querySelector('.topics-title-small');
      if (topicsSubtitle) topicsSubtitle.textContent = isArchived ? '已完成归档的选题，可在此恢复或彻底删除' : '前置准备可以自由增加、勾选和删除。正式流程保持统一，避免每条内容出现一套不同的复杂清单。';

      updateTicker();
      renderSidebar();
      renderTimeline();
      renderCards();
      // 确保 timeline 宽度正确
      setTimeout(() => {
        const timelineScroll = document.getElementById('timeline-scroll');
        const timelineInner = document.getElementById('timeline-inner');
        if (timelineScroll && timelineInner) {
          const rows = timelineInner.querySelectorAll('.timeline-row');
          let maxWidth = 0;
          rows.forEach(row => {
            maxWidth = Math.max(maxWidth, row.scrollWidth);
          });
          if (maxWidth > 0) {
            timelineInner.style.minWidth = maxWidth + 'px';
          }
        }
      }, 0);
    }

    /** ── 设置弹窗 ─────────────────────────────────────── */

    let _editingWfId = null; // 正在编辑的工作流 id

    function openSettingsModal() {
      document.getElementById('settings-modal-overlay').classList.add('open');
      switchSettingsTab('appearance');
      updateModeUI();
      updateThemeUI();
      renderWorkflowList();
    }

    function closeSettingsModal() {
      document.getElementById('settings-modal-overlay').classList.remove('open');
      _editingWfId = null;
      document.getElementById('wf-editor').style.display = 'none';
    }

    // ── 面板切换 ──
    function switchSettingsTab(tab) {
      document.querySelectorAll('.settings-tab').forEach(t => t.classList.toggle('active', t.dataset.stab === tab));
      document.querySelectorAll('.settings-panel').forEach(p => p.classList.toggle('active', p.id === 'spanel-' + tab));
    }

    // ── 主题 / 模式 ──
    function applyTheme() {
      const mode = localStorage.getItem('npiedraft-mode') || 'light';
      const theme = localStorage.getItem('npiedraft-theme') || 'warm';
      document.documentElement.setAttribute('data-theme', mode === 'dark' ? 'dark' : theme);
      if (mode === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
      else document.documentElement.setAttribute('data-theme', theme);
    }

    function updateModeUI() {
      const mode = localStorage.getItem('npiedraft-mode') || 'light';
      document.getElementById('mode-light').classList.toggle('active', mode === 'light');
      document.getElementById('mode-dark').classList.toggle('active', mode === 'dark');
      // 暗色模式下主题选项灰度不可选
      const themePanel = document.getElementById('spanel-theme');
      if (themePanel) themePanel.style.opacity = mode === 'dark' ? '0.4' : '';
      document.querySelectorAll('.theme-btn').forEach(b => {
        b.disabled = mode === 'dark';
        b.style.pointerEvents = mode === 'dark' ? 'none' : '';
      });
    }

    function updateThemeUI() {
      const theme = localStorage.getItem('npiedraft-theme') || 'warm';
      document.querySelectorAll('[data-theme-opt]').forEach(b => b.classList.remove('active'));
      const active = document.querySelector(`.theme-btn[data-theme="${theme}"]`);
      if (active) active.classList.add('active');
    }

    // ── 工作流管理 ──
    function getCustomWorkflows() {
      try { return JSON.parse(localStorage.getItem('npiedraft-custom-wf') || '[]'); } catch(_) { return []; }
    }
    function saveCustomWorkflows(wfs) { localStorage.setItem('npiedraft-custom-wf', JSON.stringify(wfs)); }

    /** 获取完整的工作流列表（内置 + 自定义） */
    function allWorkflows() {
      const builtin = [
        { id: 'self', name: '自制内容', stages: WORKFLOWS.self, isBuiltin: true },
        { id: 'commercial', name: '商单', stages: WORKFLOWS.commercial, isBuiltin: true }
      ];
      const custom = getCustomWorkflows().map(w => ({ ...w, isBuiltin: false }));
      return [...builtin, ...custom];
    }

    /** 根据 id 获取工作流定义 */
    function getWorkflowById(id) {
      if (id === 'self') return WORKFLOWS.self;
      if (id === 'commercial') return WORKFLOWS.commercial;
      const cw = getCustomWorkflows().find(w => w.id === id);
      return cw ? cw.stages : null;
    }

    function renderWorkflowList() {
      const el = document.getElementById('wf-list');
      const all = allWorkflows();
      el.innerHTML = all.map(w => `
        <div class="wf-item">
          <span class="wf-item-name">${esc(w.name)}</span>
          <span class="wf-item-tag">${w.isBuiltin ? '内置' : '自定义'} · ${w.stages.length} 节点</span>
          <div class="wf-item-actions">
            <button class="wf-icon-btn" data-wf-edit="${w.id}" title="编辑">✎</button>
            ${!w.isBuiltin ? `<button class="wf-icon-btn danger" data-wf-del="${w.id}" title="删除">✕</button>` : ''}
          </div>
        </div>
      `).join('');
      // 编辑按钮
      el.querySelectorAll('[data-wf-edit]').forEach(btn => {
        btn.addEventListener('click', () => openWorkflowEditor(btn.dataset.wfEdit));
      });
      // 删除按钮
      el.querySelectorAll('[data-wf-del]').forEach(btn => {
        btn.addEventListener('click', () => deleteWorkflow(btn.dataset.wfDel));
      });
    }

    function openWorkflowEditor(wfId) {
      _editingWfId = wfId;
      const all = allWorkflows();
      const wf = all.find(w => w.id === wfId);
      if (!wf) return;
      document.getElementById('wf-editor-name').value = wf.isBuiltin ? wf.name + '（内置，不可删）' : wf.name;
      if (wf.isBuiltin) document.getElementById('wf-editor-name').disabled = true;
      else document.getElementById('wf-editor-name').disabled = false;
      // 渲染节点编辑器
      const stagesEl = document.getElementById('wf-editor-stages');
      const stages = wf.stages.filter(s => !['cover','copy','publish'].includes(s.id));
      stagesEl.innerHTML = stages.map(s => `
        <div class="wf-stage-row">
          <input type="text" value="${esc(s.name)}" placeholder="节点名" data-wf-sname="${s.id}" />
          <input type="number" value="${s.days}" min="1" max="30" class="wf-days" placeholder="天" />
          <input type="color" value="${s.color}" title="颜色" />
          <button class="wf-icon-btn danger" data-wf-sdel="${s.id}">✕</button>
        </div>
      `).join('');
      document.getElementById('wf-editor').style.display = 'block';
    }

    function addWorkflowStageRow() {
      const stagesEl = document.getElementById('wf-editor-stages');
      const idx = Date.now();
      const row = document.createElement('div');
      row.className = 'wf-stage-row';
      row.innerHTML = `
        <input type="text" placeholder="节点名" />
        <input type="number" value="1" min="1" max="30" class="wf-days" placeholder="天" />
        <input type="color" value="#B0A090" title="颜色" />
        <button class="wf-icon-btn danger">✕</button>
      `;
      row.querySelector('.wf-icon-btn').addEventListener('click', () => row.remove());
      stagesEl.appendChild(row);
    }

    function saveWorkflowFromEditor() {
      const name = document.getElementById('wf-editor-name').value.trim();
      if (!name) { toast('请输入工作流名称'); return; }
      const rows = document.querySelectorAll('#wf-editor-stages .wf-stage-row');
      const stages = [];
      rows.forEach(row => {
        const inputs = row.querySelectorAll('input');
        const sname = inputs[0].value.trim();
        if (!sname) return;
        stages.push({
          id: 's' + Date.now() + Math.random().toString(36).slice(2,5),
          name: sname,
          days: Math.max(1, parseInt(inputs[1].value) || 1),
          color: inputs[2].value
        });
      });
      if (!stages.length) { toast('请至少添加一个节点'); return; }
      // 自动追加封面/文案/发布
      stages.push(
        { id: 'cover', name: '封面', days: 1, color: '#C8B8A0' },
        { id: 'copy', name: '文案', days: 1, color: '#D4C0B0' },
        { id: 'publish', name: '发布', days: 1, color: '#A09080' }
      );
      const customWfs = getCustomWorkflows();
      if (_editingWfId && customWfs.find(w => w.id === _editingWfId)) {
        const wf = customWfs.find(w => w.id === _editingWfId);
        wf.name = name;
        wf.stages = stages;
      } else if (_editingWfId === 'self' || _editingWfId === 'commercial') {
        // 编辑内置工作流：存为覆盖
        WORKFLOWS[_editingWfId] = stages;
        toast(`已更新「${name}」工作流`);
      } else {
        // 新建
        customWfs.push({ id: 'cw_' + Date.now(), name, stages });
      }
      saveCustomWorkflows(customWfs);
      // 更新新增选题下拉框
      updateTypeSelect();
      _editingWfId = null;
      document.getElementById('wf-editor').style.display = 'none';
      renderWorkflowList();
      toast(`已保存工作流「${name}」`);
    }

    function deleteWorkflow(wfId) {
      const customWfs = getCustomWorkflows();
      const wf = customWfs.find(w => w.id === wfId);
      if (!wf) return;
      // 检查是否有选题在使用
      const usingTopics = state.topics.filter(t => t.type === wfId && calcProgress(t) > 0);
      if (usingTopics.length) {
        alert(`无法删除：${usingTopics.length} 个选题正在使用此工作流（进度 > 0%）。请等待选题执行完毕后再删除。`);
        return;
      }
      if (!confirm(`确定删除工作流「${wf.name}」？`)) return;
      saveCustomWorkflows(customWfs.filter(w => w.id !== wfId));
      // 将使用此工作流的选题回退为自制
      state.topics.forEach(t => { if (t.type === wfId) t.type = 'self'; });
      updateTypeSelect();
      renderWorkflowList();
      save(); render();
      toast(`已删除「${wf.name}」`);
    }

    /** 更新新增选题弹窗的工作流类型下拉 */
    function updateTypeSelect() {
      const sel = document.getElementById('modal-type');
      if (!sel) return;
      const all = allWorkflows();
      sel.innerHTML = all.map(w => `<option value="${w.id}">${esc(w.name)}</option>`).join('');
      // 也更新已有选题卡里的下拉
      document.querySelectorAll('[data-type-select]').forEach(cardSel => {
        const current = cardSel.value;
        cardSel.innerHTML = all.map(w => `<option value="${w.id}" ${w.id === current ? 'selected' : ''}>${esc(w.name)}</option>`).join('');
      });
    }

    // ── 初始化主题 ──
    function initTheme() {
      if (!localStorage.getItem('npiedraft-mode')) localStorage.setItem('npiedraft-mode', 'light');
      if (!localStorage.getItem('npiedraft-theme')) localStorage.setItem('npiedraft-theme', 'warm');
      applyTheme();
      updateTypeSelect();
    }

    /** 初始化 */
    function init() {
      if (!load()) seedData();
      updateBounds();

      document.getElementById('btn-add-topic').onclick = () => openAddModal();
      document.getElementById('modal-cancel').onclick = closeModal;
      document.getElementById('modal-confirm').onclick = confirmAdd;
      document.getElementById('modal-overlay').addEventListener('click', e => {
        if (e.target.id === 'modal-overlay') closeModal();
      });
      // 星评点击
      document.querySelectorAll('#modal-priority span').forEach(star => {
        star.addEventListener('click', () => {
          const val = parseInt(star.dataset.star);
          document.getElementById('modal-priority-val').value = val;
          document.querySelectorAll('#modal-priority span').forEach((s, i) => {
            s.classList.toggle('active', i < val);
          });
        });
      });
      // 商单显示金额字段
      document.getElementById('modal-type').addEventListener('change', function() {
        document.getElementById('modal-budget-field').style.display = this.value === 'commercial' ? '' : 'none';
      });

      // 新增日程弹窗
      document.getElementById('schedule-modal-cancel').onclick  = closeScheduleModal;
      document.getElementById('schedule-modal-confirm').onclick = confirmSchedule;
      document.getElementById('schedule-modal-overlay').addEventListener('click', e => {
        if (e.target.id === 'schedule-modal-overlay') closeScheduleModal();
      });
      document.getElementById('schedule-modal-name').addEventListener('keydown', e => {
        if (e.key === 'Enter') confirmSchedule();
      });

      // Obsidian 链接弹窗
      document.getElementById('obsidian-modal-cancel').onclick  = closeObsidianModal;
      document.getElementById('obsidian-modal-confirm').onclick = confirmObsidianUrl;
      document.getElementById('obsidian-modal-clear').onclick   = () => {
        document.getElementById('obsidian-modal-input').value = '';
        confirmObsidianUrl();
      };
      document.getElementById('obsidian-modal-overlay').addEventListener('click', e => {
        if (e.target.id === 'obsidian-modal-overlay') closeObsidianModal();
      });
      document.getElementById('obsidian-modal-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') confirmObsidianUrl();
      });

      // 重命名弹窗
      document.getElementById('rename-modal-cancel').onclick  = closeRenameModal;
      document.getElementById('rename-modal-confirm').onclick = confirmRename;
      document.getElementById('rename-modal-overlay').addEventListener('click', e => {
        if (e.target.id === 'rename-modal-overlay') closeRenameModal();
      });
      document.getElementById('rename-modal-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') confirmRename();
      });

      document.getElementById('import-file').addEventListener('change', e => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
          try {
            const data = JSON.parse(ev.target.result);
            if (!Array.isArray(data.topics)) throw new Error('invalid');
            state.topics = data.topics.map(t => ({
              ...t, prep: normalizePrep(t.prep),
              archived: t.archived ?? false,
              obsidianUrl: t.obsidianUrl ?? '',
              status: t.status ?? 'normal',
              priority: t.priority ?? 0,
              budget: t.budget ?? '',
              tasks: t.tasks?.length ? t.tasks : buildWorkflow(t)
            }));
            save(); render();
            toast('导入成功');
          } catch (_) { toast('导入失败'); }
        };
        reader.readAsText(file);
        e.target.value = '';
      });

      // 设置弹窗事件
      document.getElementById('settings-modal-overlay').addEventListener('click', e => {
        if (e.target.id === 'settings-modal-overlay') closeSettingsModal();
      });
      document.getElementById('settings-modal-close').onclick = closeSettingsModal;
      document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.addEventListener('click', () => switchSettingsTab(tab.dataset.stab));
      });
      // 外观
      document.getElementById('mode-light').addEventListener('click', () => {
        localStorage.setItem('npiedraft-mode', 'light');
        applyTheme(); updateModeUI();
      });
      document.getElementById('mode-dark').addEventListener('click', () => {
        localStorage.setItem('npiedraft-mode', 'dark');
        applyTheme(); updateModeUI();
      });
      // 主题
      document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          localStorage.setItem('npiedraft-theme', btn.dataset.theme);
          applyTheme(); updateThemeUI();
        });
      });
      // 工作流
      document.getElementById('btn-add-workflow').addEventListener('click', () => {
        _editingWfId = null;
        document.getElementById('wf-editor-name').value = '';
        document.getElementById('wf-editor-name').disabled = false;
        document.getElementById('wf-editor-stages').innerHTML = '';
        document.getElementById('wf-editor').style.display = 'block';
      });
      document.getElementById('btn-wf-add-stage').addEventListener('click', addWorkflowStageRow);
      document.getElementById('btn-wf-save').addEventListener('click', saveWorkflowFromEditor);
      document.getElementById('btn-wf-cancel').addEventListener('click', () => {
        _editingWfId = null;
        document.getElementById('wf-editor').style.display = 'none';
      });
      // 初始化主题
      initTheme();

      render();
    }

    init();
