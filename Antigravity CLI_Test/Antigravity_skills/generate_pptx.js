const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Antigravity AI Assistant';
pres.title = 'OpenClaw Presentation';

// Themes & Colors (Midnight Executive)
const PRIMARY = "1E2761";   // Navy
const SECONDARY = "CADCFC"; // Ice Blue
const ACCENT = "FFFFFF";    // White
const TEXT_DARK = "1E2761";
const TEXT_LIGHT = "FFFFFF";

// Helper for Slide Header
function addSlideHeader(slide, title) {
    slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: '100%', h: 0.8, fill: { color: PRIMARY } });
    slide.addText(title, { 
        x: 0.5, y: 0.15, w: 9, h: 0.5, 
        fontSize: 32, bold: true, color: TEXT_LIGHT, 
        align: 'left', valign: 'middle' 
    });
}

// Slide 1: Title Slide
{
    let slide = pres.addSlide();
    slide.background = { color: PRIMARY };
    
    slide.addText("OpenClaw", { 
        x: 0.5, y: 1.5, w: 9, h: 1, 
        fontSize: 54, bold: true, color: TEXT_LIGHT, align: 'center' 
    });
    
    slide.addText("The Revolutionary Autonomous AI Agent", { 
        x: 0.5, y: 2.5, w: 9, h: 0.5, 
        fontSize: 24, italic: true, color: SECONDARY, align: 'center' 
    });
    
    slide.addText("Redefining Automation through Open Source Intelligence", { 
        x: 0.5, y: 3.5, w: 9, h: 0.4, 
        fontSize: 18, color: TEXT_LIGHT, align: 'center' 
    });
    
    slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.2, w: '100%', h: 0.425, fill: { color: SECONDARY } });
}

// Slide 2: What is OpenClaw?
{
    let slide = pres.addSlide();
    addSlideHeader(slide, "What is OpenClaw?");
    
    slide.addText([
        { text: "A free and open-source autonomous AI agent.", options: { bullet: true, breakLine: true } },
        { text: "Designed to execute complex tasks via LLMs (Claude, DeepSeek, GPT).", options: { bullet: true, breakLine: true } },
        { text: "Uses messaging platforms (Signal, Telegram, Discord, WhatsApp) as a primary interface.", options: { bullet: true } }
    ], { x: 0.5, y: 1.2, w: 5.5, h: 3.5, fontSize: 18, color: TEXT_DARK });

    // Decorative Graphic Placeholder (Simple shapes representing high level flow)
    slide.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 1.5, w: 2.5, h: 0.8, fill: { color: SECONDARY }, line: { color: PRIMARY, width: 2 } });
    slide.addText("USER", { x: 6.5, y: 1.5, w: 2.5, h: 0.8, align: 'center', valign: 'middle', color: PRIMARY, bold: true });
    
    slide.addShape(pres.shapes.LINE, { x: 7.75, y: 2.3, w: 0, h: 0.5, line: { color: PRIMARY, width: 2, endArrowType: 'triangle' } });
    
    slide.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 2.8, w: 2.5, h: 0.8, fill: { color: PRIMARY } });
    slide.addText("OpenClaw", { x: 6.5, y: 2.8, w: 2.5, h: 0.8, align: 'center', valign: 'middle', color: TEXT_LIGHT, bold: true });

    slide.addShape(pres.shapes.LINE, { x: 7.75, y: 3.6, w: 0, h: 0.5, line: { color: PRIMARY, width: 2, endArrowType: 'triangle' } });

    slide.addShape(pres.shapes.RECTANGLE, { x: 6.5, y: 4.1, w: 2.5, h: 0.8, fill: { color: SECONDARY }, line: { color: PRIMARY, width: 2 } });
    slide.addText("SUCCESS", { x: 6.5, y: 4.1, w: 2.5, h: 0.8, align: 'center', valign: 'middle', color: PRIMARY, bold: true });
}

// Slide 3: Core Features
{
    let slide = pres.addSlide();
    addSlideHeader(slide, "Built for Action");
    
    const features = [
        { title: "Autonomous Workflows", desc: "Plans and executes multi-step processes independently without constant supervision." },
        { title: "Deep System Access", desc: "Interacts directly with files, APIs, applications, and local system tools." },
        { title: "Adaptive Problem Solving", desc: "Solves novel technical problems in ways not explicitly programmed (Emergent Ability)." }
    ];
    
    features.forEach((f, i) => {
        let yPos = 1.2 + (i * 1.3);
        slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: yPos, w: 9, h: 1.1, fill: { color: "F8FAFC" }, line: { color: SECONDARY, width: 1 } });
        slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: yPos, w: 0.1, h: 1.1, fill: { color: PRIMARY } });
        
        slide.addText(f.title, { x: 0.7, y: yPos + 0.1, w: 8, h: 0.4, fontSize: 20, bold: true, color: PRIMARY, margin: 0 });
        slide.addText(f.desc, { x: 0.7, y: yPos + 0.5, w: 8.5, h: 0.5, fontSize: 14, color: "475569", margin: 0 });
    });
}

// Slide 4: Security & Privacy
{
    let slide = pres.addSlide();
    addSlideHeader(slide, "Local-First Intelligence");
    
    slide.addText([
        { text: "Privacy Centric", options: { bold: true, breakLine: true } },
        { text: "Configuration data and interaction history are stored strictly locally.", options: { breakLine: true } },
        { text: "", options: { breakLine: true } },
        { text: "Local Environment", options: { bold: true, breakLine: true } },
        { text: "Runs within the user's controlled environment for maximum safety.", options: { breakLine: true } },
        { text: "", options: { breakLine: true } },
        { text: "Transparency", options: { bold: true, breakLine: true } },
        { text: "Open-source codebase allows for thorough security auditing and community trust.", options: {} }
    ], { x: 0.5, y: 1.2, w: 6, h: 4, fontSize: 16, color: TEXT_DARK });
    
    // Shield Graphic
    slide.addShape(pres.shapes.OVAL, { x: 7, y: 1.5, w: 2.2, h: 2.2, fill: { color: SECONDARY }, line: { color: PRIMARY, width: 3 } });
    slide.addText("SECURE", { x: 7, y: 1.5, w: 2.2, h: 2.2, align: 'center', valign: 'middle', fontSize: 24, bold: true, color: PRIMARY });
}

// Slide 5: The OpenClaw Ecosystem
{
    let slide = pres.addSlide();
    addSlideHeader(slide, "Open Source & Future-Proof");
    
    const tech = ["TypeScript", "Swift", "SDL", "Rust"];
    const os = ["macOS", "Linux", "Windows", "Mobile"];

    slide.addText("Technologies & Platforms", { x: 0.5, y: 1.2, w: 9, h: 0.5, fontSize: 22, bold: true, color: PRIMARY });

    // Grid of tech/OS
    [...tech, ...os].forEach((item, i) => {
        let col = i % 4;
        let row = Math.floor(i / 4);
        slide.addShape(pres.shapes.RECTANGLE, { 
            x: 0.5 + (col * 2.3), y: 2.0 + (row * 1.5), w: 2, h: 1, 
            fill: { color: (row === 0 ? PRIMARY : SECONDARY) },
            line: { color: PRIMARY, width: 1 }
        });
        slide.addText(item, { 
            x: 0.5 + (col * 2.3), y: 2.0 + (row * 1.5), w: 2, h: 1, 
            align: 'center', valign: 'middle', 
            fontSize: 18, bold: true, color: (row === 0 ? TEXT_LIGHT : PRIMARY) 
        });
    });
}

// Slide 6: Conclusion
{
    let slide = pres.addSlide();
    slide.background = { color: PRIMARY };
    
    slide.addText("Join the Autonomous Future", { 
        x: 0.5, y: 1.5, w: 9, h: 1, 
        fontSize: 44, bold: true, color: SECONDARY, align: 'center' 
    });
    
    slide.addText("Empowering users with personal AI assistants that actually work.", { 
        x: 0.5, y: 2.6, w: 9, h: 0.5, 
        fontSize: 20, color: TEXT_LIGHT, align: 'center' 
    });

    slide.addShape(pres.shapes.RECTANGLE, { x: 3.5, y: 3.5, w: 3, h: 0.8, fill: { color: ACCENT }, line: { color: SECONDARY, width: 2 } });
    slide.addText("github.com/openclaw/openclaw", { 
        x: 3.5, y: 3.5, w: 3, h: 0.8, 
        align: 'center', valign: 'middle', fontSize: 14, bold: true, color: PRIMARY 
    });

    slide.addText("Questions?", { x: 0.5, y: 4.8, w: 9, h: 0.5, fontSize: 18, italic: true, color: SECONDARY, align: 'center' });
}

pres.writeFile({ fileName: "openclaw_presentation.pptx" })
    .then(fileName => console.log(`Presentation generated: ${fileName}`))
    .catch(err => console.error(err));
