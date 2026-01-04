import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";
import { listen } from "@tauri-apps/api/event";
import "./App.css";
import {
  ClipboardCopy,
  Image as ImageIcon,
  FileJson,
  Settings,
  History,
  Zap,
  Trash2,
  CheckCircle2,
  Loader2,
  PlusCircle,
  X,
  FileText,
  ArrowRight
} from "lucide-react";

type FormatType = "env" | "json" | "yaml" | "toml" | "custom";

interface CustomTemplate {
  name: string;
  content: string;
}

function App() {
  const [text, setText] = useState("");
  const [format, setFormat] = useState<FormatType>("env");
  const [result, setResult] = useState<any>(null);
  const [formattedOutput, setFormattedOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [customTemplates, setCustomTemplates] = useState<CustomTemplate[]>([]);
  const [selectedTemplateIndex, setSelectedTemplateIndex] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const [selectedHistoryItem, setSelectedHistoryItem] = useState<any>(null);
  const [historyPreviewOutput, setHistoryPreviewOutput] = useState("");
  const [historySearchQuery, setHistorySearchQuery] = useState("");

  useEffect(() => {
    loadHistory();
    loadTemplates();
  }, []);

  // Update history preview whenever the selected item or format changes
  useEffect(() => {
    if (selectedHistoryItem) {
      updateHistoryPreview(selectedHistoryItem, format, selectedTemplateIndex);
    }
  }, [selectedHistoryItem, format, selectedTemplateIndex, customTemplates]);

  async function updateHistoryPreview(item: any, currFormat: FormatType, templateIdx: number | null) {
    try {
      const output: string = await invoke("format_output", {
        vendor: item.vendor,
        baseUrl: item.base_url,
        apiKey: item.api_key,
        models: item.models || [],
        formatType: currFormat,
        customTemplate: (currFormat === 'custom' && templateIdx !== null) ? customTemplates[templateIdx].content : null
      });
      setHistoryPreviewOutput(output);
    } catch (e) { console.error(e); }
  }

  useEffect(() => {
    const unlisten = listen("tauri://drag-drop", (event: any) => {
      const paths = event.payload.paths as string[];
      if (paths.length > 0) {
        const path = paths[0];
        if (path.match(/\.(png|jpg|jpeg)$/i)) {
          processOCR(path);
        }
      }
      setIsDragging(false);
    });
    const unlistenEnter = listen("tauri://drag-over", () => setIsDragging(true));
    const unlistenLeave = listen("tauri://drag-drop-cancelled", () => setIsDragging(false));
    return () => {
      unlisten.then(u => u());
      unlistenEnter.then(u => u());
      unlistenLeave.then(u => u());
    };
  }, [result, format, selectedTemplateIndex, customTemplates]);

  async function loadHistory() {
    try {
      const items = await invoke("load_history");
      setHistory(items as any[]);
    } catch (e) { console.error(e); }
  }

  async function deleteHistoryItem(idx: number) {
    const newHistory = history.filter((_, i) => i !== idx);
    try {
      await invoke("save_history", { items: newHistory });
      setHistory(newHistory);
    } catch (e) { console.error(e); }
  }

  async function clearHistory() {
    try {
      await invoke("clear_history");
      setHistory([]);
    } catch (e) { console.error(e); }
  }

  async function loadTemplates() {
    try {
      const ts: any = await invoke("load_templates");
      setCustomTemplates(ts);
    } catch (e) { console.error(e); }
  }

  async function saveTemplates(ts: CustomTemplate[]) {
    try {
      await invoke("save_templates", { templates: ts });
      setCustomTemplates(ts);
    } catch (e) { console.error(e); }
  }

  async function handleParse() {
    setLoading(true);
    try {
      const parsed: any = await invoke("parse_text", { text });
      const finalResult = {
        ...parsed,
        models: result?.models || [],
        timestamp: Date.now()
      };
      setResult(finalResult);
      await updateFormattedOutput(finalResult, format, selectedTemplateIndex);
      await invoke("add_history_item", { item: finalResult });
      loadHistory();
    } catch (error) {
      console.error("Parse failed", error);
    } finally {
      setLoading(false);
    }
  }

  async function updateFormattedOutput(currResult: any, currFormat: FormatType, templateIdx: number | null) {
    if (!currResult) return;
    try {
      const output: string = await invoke("format_output", {
        vendor: currResult.vendor,
        baseUrl: currResult.base_url,
        apiKey: currResult.api_key,
        models: currResult.models || [],
        formatType: currFormat,
        customTemplate: (currFormat === 'custom' && templateIdx !== null) ? customTemplates[templateIdx].content : null
      });
      setFormattedOutput(output);
    } catch (e) { console.error(e); }
  }

  async function handleFormatChange(newFormat: FormatType) {
    setFormat(newFormat);
    setSelectedTemplateIndex(null);
    updateFormattedOutput(result, newFormat, null);
  }

  async function handleTemplateSelect(idx: number) {
    setSelectedTemplateIndex(idx);
    setFormat("custom");
    updateFormattedOutput(result, "custom", idx);
  }

  async function processOCR(path: string) {
    setOcrLoading(true);
    try {
      const models: string[] = await invoke("ocr_extract_models", {
        imagePath: path,
        mode: "system"
      });

      const newResult = result
        ? { ...result, models, timestamp: Date.now() }
        : { vendor: 'custom', models, base_url: '', api_key: '', timestamp: Date.now() };

      setResult(newResult);
      await updateFormattedOutput(newResult, format, selectedTemplateIndex);
      await invoke("add_history_item", { item: newResult });
      loadHistory();
    } catch (e) {
      console.error("OCR failed", e);
    } finally {
      setOcrLoading(false);
    }
  }

  async function handleOCR() {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: 'Images', extensions: ['png', 'jpg', 'jpeg'] }]
      });
      if (selected && typeof selected === 'string') {
        processOCR(selected);
      }
    } catch (e) { console.error(e); }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(formattedOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApplyHistory = (item: any) => {
    setText(item.api_key || "");
    setResult(item);
    updateFormattedOutput(item, format, selectedTemplateIndex);
    setIsHistoryModalOpen(false);
  };

  const filteredHistory = history.filter(item =>
    item.vendor.toLowerCase().includes(historySearchQuery.toLowerCase()) ||
    (item.base_url && item.base_url.toLowerCase().includes(historySearchQuery.toLowerCase()))
  );

  return (
    <div className={`flex flex-col h-screen bg-background overflow-hidden font-sans transition-all ${isDragging ? "brightness-50" : ""}`}>
      {/* Navbar */}
      <nav className="h-14 border-b border-border bg-card/30 backdrop-blur-md flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center shadow-lg shadow-primary/30">
            <FileJson className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">Format API</h1>
            <p className="text-[10px] text-muted-foreground uppercase font-semibold tracking-wider">Smart configuration engine</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {result?.models?.length > 0 && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-primary/10 border border-primary/20 text-primary animate-in fade-in slide-in-from-right-2 duration-300">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span className="text-[10px] font-bold uppercase tracking-tight">已识别 {result.models.length} 个模型</span>
              <button
                onClick={() => {
                  const nr = { ...result, models: [] };
                  setResult(nr);
                  updateFormattedOutput(nr, format, selectedTemplateIndex);
                }}
                className="ml-1 p-0.5 hover:bg-primary/20 rounded-full transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          <button
            onClick={() => setIsHistoryModalOpen(true)}
            className="p-2 rounded-xl text-muted-foreground hover:bg-muted transition-colors relative"
            title="历史记录"
          >
            <History className="w-5 h-5" />
            {history.length > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full border-2 border-background" />
            )}
          </button>
          <div className="w-[1px] h-4 bg-border mx-1" />
          <button
            onClick={() => setIsTemplateModalOpen(true)}
            className="p-2 rounded-xl text-muted-foreground hover:bg-muted transition-colors"
            title="模板管理"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {isDragging && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-primary/20 backdrop-blur-sm">
            <div className="p-12 border-2 border-dashed border-primary bg-background rounded-[3rem] shadow-2xl flex flex-col items-center gap-4 animate-in fade-in zoom-in duration-300">
              <ImageIcon className="w-20 h-20 text-primary animate-bounce" />
              <p className="font-bold text-2xl tracking-tight">Drop image to OCR</p>
            </div>
          </div>
        )}

        <header className="px-6 pt-4 pb-2 flex items-center justify-between shrink-0">
          <div>
            <h2 className="text-xs font-bold text-primary uppercase tracking-[0.2em] mb-1">Workspace</h2>
            <p className="text-sm text-muted-foreground">粘贴文本或拖入图片开始解析</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleOCR}
              disabled={ocrLoading}
              className="flex items-center gap-2 px-5 py-2.5 text-xs font-semibold rounded-2xl bg-card border border-border hover:bg-muted transition-all shadow-sm"
            >
              {ocrLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ImageIcon className="w-3.5 h-3.5 text-primary" />}
              图片识图
            </button>
            <button
              onClick={handleParse}
              disabled={loading || !text}
              className="flex items-center gap-2 px-7 py-2.5 text-xs font-bold rounded-2xl bg-primary text-primary-foreground shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              <Zap className="w-3.5 h-3.5 fill-current" />
              提取配置
            </button>
          </div>
        </header>

        <section className="flex-1 px-6 pb-6 grid grid-cols-1 lg:grid-cols-2 gap-4 overflow-hidden min-h-0">
          {/* Input Panel */}
          <div className="flex flex-col min-h-0">
            <div className="flex-1 flex flex-col rounded-2xl border border-border bg-card shadow-sm overflow-hidden focus-within:ring-4 focus-within:ring-primary/5 transition-all">
              <div className="px-4 py-2.5 border-b border-border bg-muted/20 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <FileText className="w-3.5 h-3.5 text-muted-foreground" />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Input Buffer</span>
                </div>
                <span className="text-[10px] font-mono text-muted-foreground opacity-50">{text.length} chars</span>
              </div>
              <textarea
                className="flex-1 w-full bg-transparent p-4 text-sm focus:outline-none resize-none font-mono leading-7 placeholder:italic"
                placeholder="在此粘贴包含 API Key 和 Base URL 的内容，或直接拖入包含模型的图片..."
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </div>
          </div>

          {/* Output Panel */}
          <div className="flex flex-col min-h-0">
            <div className="flex-1 flex flex-col rounded-2xl border border-border bg-[#090C14] shadow-2xl overflow-hidden group">
              <div className="px-4 py-2.5 border-b border-white/5 bg-white/[0.02] flex flex-wrap gap-2 items-center justify-between">
                <div className="flex flex-wrap gap-1.5 p-1 bg-white/[0.03] rounded-xl border border-white/5">
                  {(["env", "json", "yaml", "toml"] as FormatType[]).map((f) => (
                    <button
                      key={f}
                      onClick={() => handleFormatChange(f)}
                      className={`px-3 py-1.5 text-[10px] rounded-lg font-bold uppercase transition-all ${format === f && selectedTemplateIndex === null ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20" : "text-white/40 hover:text-white/70 hover:bg-white/5"
                        }`}
                    >
                      {f}
                    </button>
                  ))}
                  <div className="w-[1px] h-3 bg-white/10 self-center mx-1" />
                  {customTemplates.map((t, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleTemplateSelect(idx)}
                      className={`px-3 py-1.5 text-[10px] rounded-lg font-bold uppercase transition-all ${format === 'custom' && selectedTemplateIndex === idx ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20" : "text-white/40 hover:text-white/70 hover:bg-white/5"
                        }`}
                    >
                      {t.name}
                    </button>
                  ))}
                </div>
                <button
                  onClick={copyToClipboard}
                  disabled={!formattedOutput}
                  className="p-2.5 rounded-xl text-white/40 hover:text-white hover:bg-white/10 transition-all active:scale-90 group-hover:scale-110"
                >
                  {copied ? <CheckCircle2 className="w-5 h-5 text-green-400" /> : <ClipboardCopy className="w-5 h-5" />}
                </button>
              </div>
              <div className="flex-1 overflow-hidden p-4">
                {formattedOutput ? (
                  <textarea
                    className="w-full h-full bg-transparent text-[13px] font-mono text-slate-300 leading-8 selection:bg-primary/40 selection:text-white resize-none border-none outline-none custom-scrollbar"
                    value={formattedOutput}
                    onChange={(e) => setFormattedOutput(e.target.value)}
                  />
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-white/[0.05] gap-6 animate-pulse">
                    <FileJson className="w-24 h-24 stroke-[1px]" />
                    <p className="text-xs font-bold tracking-[0.3em] uppercase opacity-50">Output Ready</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* History Sidebar Drawer */}
      <div className={`fixed inset-0 z-[100] transition-opacity duration-300 ${isHistoryModalOpen ? "opacity-100" : "opacity-0 pointer-events-none"}`}>
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          onClick={() => {
            setIsHistoryModalOpen(false);
            setSelectedHistoryItem(null);
          }}
        />

        {/* Sidebar Content */}
        <div className={`absolute right-0 top-0 h-full w-full max-w-xl bg-card border-l border-border shadow-2xl transition-transform duration-500 transform ${isHistoryModalOpen ? "translate-x-0" : "translate-x-full"} flex flex-col`}>
          <header className="p-6 border-b border-border flex items-center justify-between bg-muted/5 shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-primary/10 rounded-xl text-primary">
                <History className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-bold">配置档案库</h2>
            </div>
            <button
              onClick={() => {
                setIsHistoryModalOpen(false);
                setSelectedHistoryItem(null);
              }}
              className="p-2 hover:bg-muted rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </header>

          <div className="p-4 border-b border-border bg-muted/10">
            <div className="relative">
              <input
                type="text"
                placeholder="搜索 Vendor 或 URL..."
                value={historySearchQuery}
                onChange={(e) => setHistorySearchQuery(e.target.value)}
                className="w-full bg-background border border-border rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none pr-10"
              />
              {historySearchQuery && (
                <button
                  onClick={() => setHistorySearchQuery("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          <div className="flex-1 flex overflow-hidden">
            {/* Left: List */}
            <div className="w-64 border-r border-border flex flex-col bg-muted/5">
              <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
                {filteredHistory.length > 0 ? filteredHistory.map((item, i) => (
                  <div
                    key={i}
                    onClick={() => setSelectedHistoryItem(item)}
                    onDoubleClick={() => handleApplyHistory(item)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer group relative ${selectedHistoryItem?.timestamp === item.timestamp
                      ? "bg-primary border-primary text-primary-foreground shadow-lg shadow-primary/20"
                      : "bg-background border-transparent hover:border-border hover:bg-muted/50"
                      }`}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className={`text-[9px] font-mono uppercase ${selectedHistoryItem?.timestamp === item.timestamp ? "text-primary-foreground/70" : "text-muted-foreground"}`}>{item.vendor}</span>
                      <span className={`text-[9px] opacity-60`}>{new Date(item.timestamp).toLocaleDateString()}</span>
                    </div>
                    <div className="text-[11px] font-medium truncate pr-4">{item.base_url || "识图提取"}</div>

                    <div className="absolute right-2 bottom-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteHistoryItem(i);
                          if (selectedHistoryItem?.timestamp === item.timestamp) setSelectedHistoryItem(null);
                        }}
                        className={`p-1.5 rounded-lg transition-all ${selectedHistoryItem?.timestamp === item.timestamp ? "hover:bg-white/20 text-white" : "hover:bg-destructive/10 text-muted-foreground hover:text-destructive"}`}
                        title="删除"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleApplyHistory(item);
                        }}
                        className={`p-1.5 rounded-lg transition-all ${selectedHistoryItem?.timestamp === item.timestamp ? "bg-white text-primary" : "bg-primary text-white shadow-sm"}`}
                        title="应用到编辑器"
                      >
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                )) : (
                  <div className="h-full flex flex-col items-center justify-center text-muted-foreground/30 gap-4 pt-12">
                    <History className="w-10 h-10 stroke-[1px]" />
                    <p className="text-[10px] uppercase tracking-widest">无匹配项</p>
                  </div>
                )}
              </div>
              <div className="p-3 border-t border-border mt-auto">
                <button
                  onClick={clearHistory}
                  className="w-full py-2 text-[10px] font-bold text-destructive hover:bg-destructive/10 rounded-lg transition-all border border-transparent hover:border-destructive/20 uppercase tracking-widest"
                >
                  清空全部历史
                </button>
              </div>
            </div>

            {/* Right: Detailed Preview */}
            <div className="flex-1 flex flex-col bg-background overflow-hidden">
              {selectedHistoryItem ? (
                <div className="flex-1 flex flex-col animate-in fade-in slide-in-from-right-4 duration-300 overflow-hidden">
                  <div className="p-5 border-b border-border flex flex-col gap-3 shrink-0">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-bold">详情预览</h3>
                      <button
                        onClick={() => handleApplyHistory(selectedHistoryItem)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-bold bg-primary text-primary-foreground rounded-lg shadow-lg shadow-primary/10 hover:scale-105 active:scale-95 transition-all"
                      >
                        应用配置
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-[9px] bg-muted px-2 py-0.5 rounded-full font-mono">{selectedHistoryItem.vendor}</span>
                      <span className="text-[9px] bg-muted px-2 py-0.5 rounded-full">{new Date(selectedHistoryItem.timestamp).toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="flex-1 overflow-y-auto p-5 custom-scrollbar space-y-4">
                    <div className="space-y-2">
                      <div className="p-3 rounded-xl bg-muted/20 border border-border group relative">
                        <p className="text-[9px] font-bold text-muted-foreground uppercase mb-1">Base URL</p>
                        <p className="text-xs font-mono break-all line-clamp-2 pr-8">{selectedHistoryItem.base_url || "N/A"}</p>
                        {selectedHistoryItem.base_url && (
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(selectedHistoryItem.base_url);
                              setCopied(true);
                              setTimeout(() => setCopied(false), 2000);
                            }}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-muted-foreground hover:text-primary opacity-0 group-hover:opacity-100 transition-all"
                          >
                            <ClipboardCopy className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                      <div className="p-3 rounded-xl bg-muted/20 border border-border group relative">
                        <p className="text-[9px] font-bold text-muted-foreground uppercase mb-1">API Key</p>
                        <p className="text-xs font-mono break-all line-clamp-2 pr-8">{selectedHistoryItem.api_key || "N/A"}</p>
                        {selectedHistoryItem.api_key && (
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(selectedHistoryItem.api_key);
                              setCopied(true);
                              setTimeout(() => setCopied(false), 2000);
                            }}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-muted-foreground hover:text-primary opacity-0 group-hover:opacity-100 transition-all"
                          >
                            <ClipboardCopy className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                      <div className="p-3 rounded-xl bg-muted/20 border border-border">
                        <p className="text-[9px] font-bold text-muted-foreground uppercase mb-1">Models</p>
                        <p className="text-xs font-mono">{selectedHistoryItem.models?.length || 0} items identified</p>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-border bg-[#090C14] overflow-hidden flex flex-col">
                      <div className="px-4 py-2 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
                        <span className="text-[9px] font-bold uppercase tracking-widest text-white/40">预览输出 ({format})</span>
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(historyPreviewOutput);
                            setCopied(true);
                            setTimeout(() => setCopied(false), 2000);
                          }}
                          className="p-1.5 text-white/40 hover:text-white transition-all"
                        >
                          {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-green-400" /> : <ClipboardCopy className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                      <div className="p-4 overflow-x-auto">
                        <pre className="text-[11px] font-mono text-slate-300 leading-6 whitespace-pre-wrap break-all">
                          {historyPreviewOutput}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-muted-foreground/20 gap-4">
                  <ArrowRight className="w-16 h-16 stroke-[0.5px] -rotate-45" />
                  <p className="text-[10px] font-bold uppercase tracking-[0.3em]">选择侧边档案</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Template Management Modal */}
      {isTemplateModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-xl animate-in fade-in duration-300">
          <div className="bg-card border border-border w-full max-w-2xl rounded-[3rem] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in duration-300">
            <header className="p-8 border-b border-border flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold">自定义导出格式</h2>
                <div className="flex gap-3 text-[10px] text-muted-foreground mt-2 font-mono">
                  <span className="bg-secondary px-1.5 py-0.5 rounded">{"{{api_key}}"}</span>
                  <span className="bg-secondary px-1.5 py-0.5 rounded">{"{{base_url}}"}</span>
                  <span className="bg-secondary px-1.5 py-0.5 rounded">{"{{models_comma}}"}</span>
                </div>
              </div>
              <button onClick={() => setIsTemplateModalOpen(false)} className="p-3 hover:bg-muted rounded-full transition-colors">
                <X className="w-6 h-6" />
              </button>
            </header>
            <div className="p-8 flex-1 overflow-y-auto space-y-6 max-h-[60vh] custom-scrollbar">
              {customTemplates.map((t, idx) => (
                <div key={idx} className="p-6 rounded-[2rem] bg-muted/20 border border-border group relative transition-all hover:bg-muted/30">
                  <div className="flex gap-4 items-start mb-6">
                    <input
                      className="flex-1 bg-transparent border-b border-transparent text-sm font-bold focus:border-primary outline-none py-1 transition-colors"
                      value={t.name}
                      placeholder="模板名称 (如: Cursor 专用)"
                      onChange={(e) => {
                        const newTs = [...customTemplates];
                        newTs[idx].name = e.target.value;
                        setCustomTemplates(newTs);
                      }}
                    />
                    <button
                      onClick={() => {
                        const newTs = customTemplates.filter((_, i) => i !== idx);
                        saveTemplates(newTs);
                      }}
                      className="p-1 text-muted-foreground hover:text-destructive transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex justify-between items-center mb-2 px-1">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Template Source</span>
                    <button
                      onClick={() => {
                        let c = t.content;
                        c = c.replace(/sk-[a-zA-Z0-9]{20,}/g, "{{api_key}}");
                        c = c.replace(/(?:key|apiKey|api_key)[:=]\s*["']?([a-zA-Z0-9]{32,})["']?/gi, (match, p1) => match.replace(p1, "{{api_key}}"));
                        c = c.replace(/https?:\/\/[a-zA-Z0-9.\-/_]+/g, "{{base_url}}");
                        c = c.replace(/^(MODELS?[:=]\s*)\[\s*".*?"(?:,\s*".*?")*\s*\]$/gmi, "$1{{models}}");
                        c = c.replace(/^(MODELS?[:=]\s*)(?!\{\{)(.+)$/gmi, "$1{{models_comma}}");
                        const newTs = [...customTemplates];
                        newTs[idx].content = c;
                        setCustomTemplates(newTs);
                      }}
                      className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-primary/20 text-primary text-[10px] font-bold hover:bg-primary/30 transition-all border border-primary/30"
                    >
                      <Zap className="w-3 h-3 fill-current" />
                      智能转换为模板
                    </button>
                  </div>

                  <textarea
                    className="w-full bg-background border border-border rounded-2xl p-4 text-xs font-mono focus:ring-2 focus:ring-primary/20 outline-none leading-relaxed"
                    rows={4}
                    value={t.content}
                    placeholder="在此粘贴参考配置，点击上方智能识别..."
                    onChange={(e) => {
                      const newTs = [...customTemplates];
                      newTs[idx].content = e.target.value;
                      setCustomTemplates(newTs);
                    }}
                  />
                </div>
              ))}
              <button
                onClick={() => {
                  const newTs = [...customTemplates, { name: "新模板", content: "BASE_URL={{base_url}}\nAPI_KEY={{api_key}}" }];
                  setCustomTemplates(newTs);
                }}
                className="w-full py-8 rounded-[2rem] border-2 border-dashed border-border hover:border-primary/50 hover:bg-primary/5 text-muted-foreground hover:text-primary transition-all flex flex-col items-center justify-center gap-2"
              >
                <PlusCircle className="w-8 h-8 opacity-20" />
                <span className="text-sm font-bold uppercase tracking-widest opacity-50">Create Format</span>
              </button>
            </div>
            <footer className="p-8 border-t border-border flex justify-end gap-3 bg-muted/10">
              <button onClick={() => {
                loadTemplates();
                setIsTemplateModalOpen(false);
              }} className="px-8 py-3 text-sm font-semibold hover:bg-muted transition-colors rounded-2xl">弃用更改</button>
              <button onClick={() => {
                saveTemplates(customTemplates);
                setIsTemplateModalOpen(false);
              }} className="px-10 py-3 text-sm font-bold bg-primary text-primary-foreground rounded-[1.25rem] shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all">保存全部</button>
            </footer>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
