import { useEffect, useState } from "react";
import {
  Activity,
  ArrowDownRight,
  BriefcaseBusiness,
  Command,
  ExternalLink,
  Download,
  FolderOpen,
  Globe2,
  LayoutDashboard,
  MapPin,
  Plus,
  Settings,
  Sparkles,
  Monitor,
  RefreshCw,
  Smartphone,
  Trash2,
} from "lucide-react";
import BusinessOnboarding from "./components/BusinessOnboarding";
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

type Page = "Dashboard" | "Websites" | "Settings" | "Create" | "Preview";
type DesignId =
  | "modern-minimal"
  | "bold-vibrant"
  | "premium-elegant";

const DESIGN_OPTIONS: {
  id: DesignId;
  name: string;
  description: string;
  background: string;
  accent: string;
}[] = [
  {
    id: "modern-minimal",
    name: "Modern Minimal",
    description: "Clean, professional and spacious.",
    background: "bg-slate-100",
    accent: "bg-blue-600",
  },
  {
    id: "bold-vibrant",
    name: "Bold & Vibrant",
    description: "Expressive colours and energetic layouts.",
    background: "bg-orange-100",
    accent: "bg-orange-600",
  },
  {
    id: "premium-elegant",
    name: "Premium Elegant",
    description: "Refined typography and understated luxury.",
    background: "bg-stone-200",
    accent: "bg-stone-800",
  },
];

interface BusinessRecord {
  id: string;
  business_name: string;
  category: string;
  location: string;
  phone?: string | null;
  email?: string | null;
  created_at: string;
}

function App() {
  const [page, setPage] = useState<Page>("Dashboard");
  const [backend, setBackend] = useState<"checking" | "connected" | "offline">(
    "checking"
  );
  const [previewBusiness, setPreviewBusiness] =
    useState<BusinessRecord | null>(null);

  useEffect(() => {
    let mounted = true;

    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/businesses`);
        if (!response.ok) throw new Error("Backend unavailable");

        if (mounted) setBackend("connected");
      } catch {
        if (mounted) setBackend("offline");
      }
    };

    checkBackend();
    const interval = window.setInterval(checkBackend, 5000);

    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  const navigation = [
    { name: "Dashboard" as Page, icon: LayoutDashboard },
    { name: "Websites" as Page, icon: Globe2 },
    { name: "Settings" as Page, icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-[#0a0c09] text-zinc-100">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="hidden w-[238px] shrink-0 flex-col border-r border-white/[0.07] bg-[#0e100d] px-5 py-6 md:flex">
          <div className="mb-12 flex items-center gap-3 px-1">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-lime-300 text-black shadow-lg shadow-lime-300/10">
              <Command size={23} strokeWidth={2.5} />
            </div>

            <div>
              <h1 className="text-lg font-bold tracking-tight">BizCraft</h1>
              <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
                Website Studio
              </p>
            </div>
          </div>

          <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-zinc-600">
            Workspace
          </p>

          <nav className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = page === item.name;

              return (
                <button
                  key={item.name}
                  onClick={() => setPage(item.name)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-sm transition ${
                    active
                      ? "bg-white/[0.08] font-medium text-white"
                      : "text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-200"
                  }`}
                >
                  <Icon size={18} />
                  {item.name}
                  {active && (
                    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-lime-300" />
                  )}
                </button>
              );
            })}
          </nav>

          <div className="mt-auto space-y-4">
            <div className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-4">
              <div className="mb-3 flex items-center gap-2">
                <Sparkles size={16} className="text-lime-300" />
                <span className="text-xs font-semibold text-zinc-200">
                  Built for businesses
                </span>
              </div>
              <p className="text-xs leading-5 text-zinc-500">
                Professional websites for local businesses, without the
                complexity.
              </p>
            </div>

            <div className="flex items-center gap-3 border-t border-white/[0.07] pt-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-zinc-800 text-sm font-semibold text-zinc-300">
                B
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">Local workspace</p>
                <p className="text-xs text-zinc-600">BizCraft V1</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Main content */}
        <main className="min-w-0 flex-1">
          {/* Top bar */}
          <header className="flex h-[72px] items-center justify-between border-b border-white/[0.07] px-5 sm:px-8 lg:px-10">
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <span className="md:hidden font-bold text-white">BizCraft</span>
              <span className="hidden md:inline">Workspace</span>
              <span className="hidden md:inline">/</span>
              <span className="font-medium text-zinc-200">{page}</span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 rounded-full border border-white/[0.07] bg-white/[0.025] px-3 py-1.5">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    backend === "connected"
                      ? "bg-lime-400"
                      : backend === "offline"
                        ? "bg-red-400"
                        : "bg-yellow-400"
                  }`}
                />
                <span className="text-[11px] text-zinc-400">
                  API {backend}
                </span>
              </div>

              <span className="hidden rounded-md border border-white/[0.07] px-2.5 py-1.5 text-[10px] font-medium uppercase tracking-[0.12em] text-zinc-500 sm:inline-flex">
                V1 workspace
              </span>
            </div>
          </header>

          <div className="mx-auto max-w-[1400px] px-5 py-8 pb-28 sm:px-8 lg:px-10 lg:py-10">
            {page === "Dashboard" && (
              <Dashboard
                onNavigate={setPage}
                onCreate={() => setPage("Create")}
              />
            )}

            {page === "Websites" && (
              <Websites
                onPreview={(business) => {
                  setPreviewBusiness(business);
                  setPage("Preview");
                }}
              />
            )}

            {page === "Preview" && previewBusiness && (
              <WebsitePreview
                business={previewBusiness}
                onBack={() => setPage("Websites")}
              />
            )}

            {page === "Settings" && <SettingsPage backend={backend} />}

            {page === "Create" && (
              <BusinessOnboarding
                onBack={() => setPage("Dashboard")}
                onSaved={() => setPage("Websites")}
              />
            )}
          </div>
        </main>
      </div>

      {/* Mobile navigation */}
      <div className="fixed bottom-0 left-0 right-0 z-20 flex justify-around border-t border-white/[0.08] bg-[#10130f]/95 px-2 py-3 backdrop-blur-lg md:hidden">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.name}
              onClick={() => setPage(item.name)}
              className={`flex flex-col items-center gap-1 text-[10px] ${
                page === item.name ? "text-lime-300" : "text-zinc-500"
              }`}
            >
              <Icon size={19} />
              {item.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Dashboard({
  onNavigate,
  onCreate,
}: {
  onNavigate: (page: Page) => void;
  onCreate: () => void;
}) {
  const [businesses, setBusinesses] = useState<BusinessRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadBusinesses() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/businesses`);
        if (!response.ok) throw new Error("Could not load your businesses.");
        const data: BusinessRecord[] = await response.json();
        if (mounted) {
          setBusinesses(data);
          setLoadError("");
        }
      } catch (error) {
        if (mounted) {
          setLoadError(
            error instanceof Error ? error.message : "Something went wrong."
          );
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadBusinesses();
    return () => {
      mounted = false;
    };
  }, []);

  const recentBusinesses = [...businesses].reverse().slice(0, 3);

  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#11140f] px-6 py-8 sm:px-9 sm:py-10 lg:px-11">
        <div className="pointer-events-none absolute -right-24 -top-28 h-80 w-80 rounded-full bg-lime-300/[0.07] blur-3xl" />
        <div className="relative grid gap-10 lg:grid-cols-[1.35fr_0.65fr] lg:items-end">
          <div className="max-w-2xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-lime-300/20 bg-lime-300/[0.07] px-3 py-1.5 text-[11px] font-medium text-lime-200">
              <span className="h-1.5 w-1.5 rounded-full bg-lime-300" />
              A website studio for local businesses
            </div>
            <h2 className="max-w-xl text-3xl font-semibold leading-[1.12] tracking-tight text-white sm:text-4xl lg:text-[2.8rem]">
              Turn a business into a{" "}
              <span className="text-lime-200">better web presence.</span>
            </h2>
            <p className="mt-4 max-w-lg text-sm leading-6 text-zinc-400 sm:text-[15px]">
              Bring the business details. BizCraft helps shape the content,
              choose a visual direction and generate a website you can preview
              and export.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <button
                onClick={onCreate}
                className="inline-flex items-center gap-2 rounded-lg bg-lime-300 px-5 py-3 text-sm font-semibold text-zinc-950 transition hover:bg-lime-200 focus:outline-none focus:ring-2 focus:ring-lime-200 focus:ring-offset-2 focus:ring-offset-[#11140f]"
              >
                <Plus size={17} />
                Create a website
              </button>
              <button
                onClick={() => onNavigate("Websites")}
                className="rounded-lg border border-white/10 px-5 py-3 text-sm font-medium text-zinc-300 transition hover:border-white/20 hover:bg-white/[0.04] hover:text-white"
              >
                View businesses
              </button>
            </div>
          </div>

          <div className="relative rounded-xl border border-white/[0.08] bg-black/20 p-5 sm:p-6">
            <div className="mb-5 flex items-center justify-between">
              <span className="text-xs font-medium text-zinc-300">
                The workflow
              </span>
              <span className="text-[10px] text-zinc-600">3 steps</span>
            </div>
            <div className="space-y-4">
              {[
                {
                  number: "01",
                  title: "Add business details",
                  detail: "Use a Maps link or enter them manually.",
                },
                {
                  number: "02",
                  title: "Choose a direction",
                  detail: "Pick a design that fits the business.",
                },
                {
                  number: "03",
                  title: "Generate and export",
                  detail: "Preview the site, then download its files.",
                },
              ].map((step, index) => (
                <div key={step.number} className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-lime-300/20 bg-lime-300/[0.08] text-[11px] font-semibold text-lime-200">
                    {step.number}
                  </div>
                  <div className="min-w-0 flex-1 pb-4">
                    <p className="text-sm font-medium text-zinc-200">
                      {step.title}
                    </p>
                    <p className="mt-1 text-xs leading-5 text-zinc-500">
                      {step.detail}
                    </p>
                  </div>
                  {index < 2 && <div className="sr-only">Next step</div>}
                </div>
              ))}
            </div>
            <div className="mt-1 border-t border-white/[0.07] pt-4 text-[11px] text-zinc-500">
              No hosting lock-in. Your generated files are yours to keep.
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-white/[0.07] bg-[#10120f] p-5">
          <div className="flex items-center justify-between text-xs text-zinc-500">
            Saved businesses{" "}
            <BriefcaseBusiness size={16} className="text-zinc-600" />
          </div>
          <p className="mt-4 text-3xl font-semibold tracking-tight text-white">
            {loading ? "—" : businesses.length}
          </p>
          <p className="mt-1 text-xs text-zinc-600">
            Business profiles in your workspace
          </p>
        </div>
        <div className="rounded-xl border border-white/[0.07] bg-[#10120f] p-5">
          <div className="flex items-center justify-between text-xs text-zinc-500">
            Design directions{" "}
            <Sparkles size={16} className="text-zinc-600" />
          </div>
          <p className="mt-4 text-3xl font-semibold tracking-tight text-white">
            03
          </p>
          <p className="mt-1 text-xs text-zinc-600">
            Three starting points for the look
          </p>
        </div>
        <div className="rounded-xl border border-white/[0.07] bg-[#10120f] p-5">
          <div className="flex items-center justify-between text-xs text-zinc-500">
            Website output <Globe2 size={16} className="text-zinc-600" />
          </div>
          <p className="mt-4 text-3xl font-semibold tracking-tight text-white">
            HTML
          </p>
          <p className="mt-1 text-xs text-zinc-600">
            Static files with ZIP export
          </p>
        </div>
      </section>

      <section>
        <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold tracking-tight text-white">
              Recent businesses
            </h3>
            <p className="mt-1 text-sm text-zinc-500">
              Pick up where you left off.
            </p>
          </div>
          <button
            onClick={() => onNavigate("Websites")}
            className="text-sm font-medium text-lime-200 transition hover:text-lime-100"
          >
            All businesses <span aria-hidden="true">→</span>
          </button>
        </div>

        {loading ? (
          <div className="rounded-xl border border-white/[0.07] bg-[#10120f] px-5 py-10 text-center text-sm text-zinc-500">
            Loading your workspace…
          </div>
        ) : loadError ? (
          <div
            role="alert"
            className="rounded-xl border border-red-400/20 bg-red-400/[0.06] px-5 py-4 text-sm text-red-300"
          >
            {loadError}
          </div>
        ) : recentBusinesses.length === 0 ? (
          <div className="flex flex-col items-start rounded-xl border border-dashed border-white/[0.12] bg-white/[0.015] px-6 py-8 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white/[0.05] text-zinc-400">
                <FolderOpen size={21} />
              </div>
              <div>
                <h4 className="text-sm font-medium text-zinc-200">
                  Your first project starts with a business
                </h4>
                <p className="mt-1 max-w-md text-sm leading-5 text-zinc-500">
                  Add a business profile to begin building its website. Saved
                  businesses will show up here.
                </p>
              </div>
            </div>
            <button
              onClick={onCreate}
              className="mt-5 rounded-lg border border-white/10 px-4 py-2.5 text-sm font-medium text-zinc-200 transition hover:bg-white/[0.05] sm:mt-0"
            >
              Add a business
            </button>
          </div>
        ) : (
          <div className="overflow-hidden rounded-xl border border-white/[0.07] bg-[#10120f]">
            {recentBusinesses.map((business, index) => (
              <div
                key={business.id}
                className={`flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between ${
                  index > 0 ? "border-t border-white/[0.06]" : ""
                }`}
              >
                <div className="flex min-w-0 items-center gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-lime-300/[0.08] text-lime-200">
                    <BriefcaseBusiness size={18} />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-zinc-200">
                      {business.business_name}
                    </p>
                    <p className="mt-1 truncate text-xs text-zinc-500">
                      {business.category || "Business"}
                      {business.location ? ` · ${business.location}` : ""}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => onNavigate("Websites")}
                  className="self-start text-xs font-medium text-zinc-400 transition hover:text-lime-200 sm:self-auto"
                >
                  Open in websites <span aria-hidden="true">→</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-white/[0.07] pt-5 text-xs text-zinc-600">
        <span>BizCraft · Website studio for local businesses</span>
        <span>V1 · Static website generation</span>
      </footer>
    </div>
  );
}


function Websites({
  onPreview,
}: {
  onPreview: (business: BusinessRecord) => void;
}) {
  const [businesses, setBusinesses] = useState<BusinessRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [generationError, setGenerationError] = useState("");
  const [generatingId, setGeneratingId] = useState<string | null>(null);
  const [selectedDesigns, setSelectedDesigns] = useState<
    Record<string, DesignId>
  >({});

  // Bulk management states
  const [manageMode, setManageMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadBusinesses() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/businesses`
        );

        if (!response.ok) {
          throw new Error("Could not load saved businesses.");
        }

        const data: BusinessRecord[] = await response.json();

        if (mounted) {
          setBusinesses(data);
          setError("");
        }
      } catch (err) {
        if (mounted) {
          setError(
            err instanceof Error ? err.message : "Something went wrong."
          );
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadBusinesses();

    return () => {
      mounted = false;
    };
  }, []);

  // Generate website
  async function handleGenerate(business: BusinessRecord) {
    setGeneratingId(business.id);
    setGenerationError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/businesses/${business.id}/generate?design_id=${
          selectedDesigns[business.id] ?? "modern-minimal"
        }`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Website generation failed."
        );
      }

      onPreview(business);
    } catch (err) {
      setGenerationError(
        err instanceof Error
          ? err.message
          : "Something went wrong during generation."
      );
    } finally {
      setGeneratingId(null);
    }
  }

  // Select or deselect one business
  function toggleSelection(id: string) {
    setSelectedIds((previous) =>
      previous.includes(id)
        ? previous.filter((item) => item !== id)
        : [...previous, id]
    );
  }

  // Select all or deselect all
  function toggleSelectAll() {
    if (selectedIds.length === businesses.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(businesses.map((business) => business.id));
    }
  }

  // Delete selected businesses
  async function handleBulkDelete() {
    if (selectedIds.length === 0 || deleting) return;

    setDeleting(true);
    setDeleteError("");

    const idsToDelete = [...selectedIds];

    const results = await Promise.allSettled(
      idsToDelete.map(async (id) => {
        const response = await fetch(
          `${API_BASE_URL}/api/businesses/${id}`,
          {
            method: "DELETE",
          }
        );

        if (!response.ok) {
          const data = await response.json().catch(() => ({}));

          throw new Error(
            data.detail || `Could not delete business ${id}.`
          );
        }

        return id;
      })
    );

    const deletedIds: string[] = [];
    const failedIds: string[] = [];

    results.forEach((result, index) => {
      if (result.status === "fulfilled") {
        deletedIds.push(result.value);
      } else {
        failedIds.push(idsToDelete[index]);
      }
    });

    // Remove successfully deleted businesses from the UI
    setBusinesses((previous) =>
      previous.filter((business) => !deletedIds.includes(business.id))
    );

    // Keep failed businesses selected so they can be retried
    setSelectedIds(failedIds);
    setShowDeleteConfirm(false);

    if (failedIds.length > 0) {
      setDeleteError(
        `${deletedIds.length} deleted successfully. ${failedIds.length} failed. You can retry the selected businesses.`
      );
    } else {
      setManageMode(false);
    }

    setDeleting(false);
  }

  return (
    <section className="space-y-6">

      {/* Page heading and management controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-lime-300">
            Workspace
          </p>

          <h2 className="text-3xl font-semibold tracking-tight">
            Your websites
          </h2>

          <p className="mt-2 text-sm text-zinc-500">
            Generate and preview websites for your saved businesses.
          </p>
        </div>

        {businesses.length > 0 && !loading && !error && (
          <div className="flex flex-wrap items-center gap-2">
            {manageMode && (
              <>
                <button
                  onClick={toggleSelectAll}
                  disabled={deleting}
                  className="rounded-lg border border-white/10 px-3 py-2 text-xs text-zinc-300 transition hover:bg-white/5 disabled:opacity-50"
                >
                  {selectedIds.length === businesses.length
                    ? "Deselect all"
                    : "Select all"}
                </button>

                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={selectedIds.length === 0 || deleting}
                  className="flex items-center gap-2 rounded-lg bg-red-500/10 px-3 py-2 text-xs font-semibold text-red-400 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Trash2 size={14} />
                  Delete selected ({selectedIds.length})
                </button>
              </>
            )}

            <button
              onClick={() => {
                setManageMode((previous) => !previous);
                setSelectedIds([]);
                setDeleteError("");
              }}
              disabled={deleting}
              className="rounded-lg border border-white/10 px-3 py-2 text-xs font-medium text-zinc-300 transition hover:bg-white/5 disabled:opacity-50"
            >
              {manageMode ? "Cancel" : "Manage"}
            </button>
          </div>
        )}
      </div>

      {/* Error messages */}
      {generationError && (
        <div
          role="alert"
          className="rounded-xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-300"
        >
          {generationError}
        </div>
      )}

      {deleteError && (
        <div
          role="alert"
          className="rounded-xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-300"
        >
          {deleteError}
        </div>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="flex min-h-[200px] items-center justify-center text-sm text-zinc-500">
          Loading businesses...
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-400/20 bg-red-400/10 p-5 text-sm text-red-300">
          {error}
        </div>
      ) : businesses.length === 0 ? (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-xl border border-dashed border-white/[0.1] p-8 text-center">
          <FolderOpen size={28} className="mb-4 text-zinc-600" />

          <h3 className="font-medium">No businesses yet</h3>

          <p className="mt-2 max-w-sm text-xs leading-5 text-zinc-600">
            Add a business profile to choose a design and generate its website.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">

          {/* Business cards */}
          {businesses.map((business) => {
            const isGenerating = generatingId === business.id;
            const selectedDesign =
              selectedDesigns[business.id] ?? "modern-minimal";
            const isSelected = selectedIds.includes(business.id);

            return (
              <div
                key={business.id}
                className={`rounded-xl border bg-[#101014] p-5 transition ${
                  isSelected
                    ? "border-lime-300/50 bg-lime-300/[0.025]"
                    : "border-white/[0.08]"
                }`}
              >
                {/* Business header */}
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex items-center gap-3">

                    {manageMode && (
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelection(business.id)}
                        disabled={deleting}
                        aria-label={`Select ${business.business_name}`}
                        className="h-4 w-4 cursor-pointer accent-lime-300"
                      />
                    )}

                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-lime-300/10 text-lime-300">
                      <BriefcaseBusiness size={20} />
                    </div>
                  </div>

                  <span className="rounded-full border border-white/[0.08] px-3 py-1 text-[10px] text-zinc-500">
                    Business saved
                  </span>
                </div>

                {/* Business details */}
                <h3 className="text-base font-semibold">
                  {business.business_name}
                </h3>

                <p className="mt-1 text-xs text-zinc-500">
                  {business.category}
                </p>

                <div className="mt-4 space-y-2 border-t border-white/[0.07] pt-4 text-xs text-zinc-500">
                  <p className="flex items-center gap-2">
                    <MapPin size={14} />
                    {business.location}
                  </p>

                  {business.phone && <p>{business.phone}</p>}
                  {business.email && <p>{business.email}</p>}
                </div>

                {/* Hide design and generation controls in Manage mode */}
                {!manageMode && (
                  <>
                    {/* Design selection */}
                    <div className="mt-5 border-t border-white/[0.07] pt-5">
                      <div className="mb-3">
                        <h4 className="text-sm font-semibold text-zinc-200">
                          Choose your design
                        </h4>

                        <p className="mt-1 text-[11px] text-zinc-500">
                          Select a visual direction for this website.
                        </p>
                      </div>

                      <div className="grid grid-cols-3 gap-2">
                        {DESIGN_OPTIONS.map((design) => {
                          const selected = selectedDesign === design.id;

                          return (
                            <button
                              key={design.id}
                              type="button"
                              aria-pressed={selected}
                              disabled={generatingId !== null}
                              onClick={() =>
                                setSelectedDesigns((previous) => ({
                                  ...previous,
                                  [business.id]: design.id,
                                }))
                              }
                              className={`rounded-lg border p-2 text-left transition ${
                                selected
                                  ? "border-lime-300 bg-lime-300/[0.08]"
                                  : "border-white/[0.08] bg-white/[0.02] hover:border-white/20"
                              }`}
                            >
                              <div
                                className={`mb-2 h-12 overflow-hidden rounded ${design.background} p-2`}
                              >
                                <div className="mb-1 h-1.5 w-8 rounded-full bg-black/70" />

                                <div
                                  className={`h-3 w-3/4 rounded-sm ${design.accent}`}
                                />

                                <div className="mt-1 h-1 w-1/2 rounded-full bg-black/20" />

                                <div className="mt-1 flex gap-1">
                                  <div className="h-2 w-5 rounded-sm bg-black/15" />
                                  <div className="h-2 w-5 rounded-sm bg-black/15" />
                                </div>
                              </div>

                              <p className="text-[10px] font-semibold leading-4 text-zinc-200">
                                {design.name}
                              </p>

                              <p className="mt-1 text-[9px] leading-3 text-zinc-500">
                                {design.description}
                              </p>

                              {selected && (
                                <p className="mt-2 text-[9px] font-semibold text-lime-300">
                                  ✓ Selected
                                </p>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Generate button */}
                    <button
                      type="button"
                      onClick={() => handleGenerate(business)}
                      disabled={generatingId !== null}
                      className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-lime-300 px-4 py-3 text-xs font-semibold text-black transition hover:bg-lime-200 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {isGenerating ? (
                        <>
                          <RefreshCw size={15} className="animate-spin" />
                          Generating website...
                        </>
                      ) : (
                        <>
                          <Sparkles size={15} />
                          Generate with{" "}
                          {DESIGN_OPTIONS.find(
                            (design) => design.id === selectedDesign
                          )?.name}
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Bulk deletion confirmation dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-dialog-title"
            className="w-full max-w-md rounded-2xl border border-white/10 bg-[#151713] p-6 shadow-2xl"
          >
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-red-500/10 text-red-400">
              <Trash2 size={21} />
            </div>

            <h3
              id="delete-dialog-title"
              className="text-lg font-semibold text-white"
            >
              Delete selected businesses?
            </h3>

            <p className="mt-2 text-sm leading-6 text-zinc-400">
              You are about to permanently delete {selectedIds.length} business
              {selectedIds.length !== 1 ? "es" : ""}, including their saved
              profiles and generated website files. This cannot be undone.
            </p>

            <div className="mt-6 flex justify-end gap-3">
              <button
                disabled={deleting}
                onClick={() => setShowDeleteConfirm(false)}
                className="rounded-lg border border-white/10 px-4 py-2.5 text-sm text-zinc-300 transition hover:bg-white/5 disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                disabled={deleting}
                onClick={handleBulkDelete}
                className="flex items-center gap-2 rounded-lg bg-red-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-400 disabled:opacity-50"
              >
                <Trash2 size={15} />
                {deleting ? "Deleting..." : "Delete permanently"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}


function WebsitePreview({
  business,
  onBack,
}: {
  business: BusinessRecord;
  onBack: () => void;
}) {
  const [view, setView] = useState<"desktop" | "mobile">("desktop");
  const [refreshKey, setRefreshKey] = useState(0);

  const previewUrl =
    `${API_BASE_URL}/api/businesses/${business.id}/preview/index.html`;

  return (
    <section className="space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <button
            onClick={onBack}
            className="mb-4 flex items-center gap-2 text-xs text-zinc-500 transition hover:text-white"
          >
            <ArrowDownRight size={14} className="rotate-45" />
            Back to websites
          </button>

          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-lime-300">
            Website preview
          </p>

          <h2 className="mt-2 text-2xl font-semibold tracking-tight">
            {business.business_name}
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setView("desktop")}
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs transition ${
              view === "desktop"
                ? "border-lime-300/30 bg-lime-300/10 text-lime-300"
                : "border-white/10 text-zinc-500 hover:text-white"
            }`}
          >
            <Monitor size={15} />
            Desktop
          </button>

          <button
            onClick={() => setView("mobile")}
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs transition ${
              view === "mobile"
                ? "border-lime-300/30 bg-lime-300/10 text-lime-300"
                : "border-white/10 text-zinc-500 hover:text-white"
            }`}
          >
            <Smartphone size={15} />
            Mobile
          </button>

          <button
            onClick={() => setRefreshKey((previous) => previous + 1)}
            aria-label="Refresh preview"
            className="rounded-lg border border-white/10 p-2 text-zinc-400 transition hover:text-white"
          >
            <RefreshCw size={15} />
          </button>

          <a
            href={`${API_BASE_URL}/api/businesses/${business.id}/export`}
            download
            className="flex items-center gap-2 rounded-lg border border-lime-300/30 bg-lime-300/10 px-3 py-2 text-xs font-semibold text-lime-300 transition hover:bg-lime-300/20"
          >
            <Download size={14} />
            Download ZIP
          </a>

          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-lg bg-lime-300 px-3 py-2 text-xs font-semibold text-black transition hover:bg-lime-200"
          >
            <ExternalLink size={14} />
            Open in tab
          </a>
        </div>
      </div>

      {/* Preview browser */}
      <div className="overflow-hidden rounded-xl border border-white/[0.09] bg-[#17171b]">
        <div className="flex h-11 items-center gap-2 border-b border-white/[0.07] px-4">
          <span className="h-2.5 w-2.5 rounded-full bg-red-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-lime-400/80" />

          <div className="ml-3 min-w-0 flex-1 truncate rounded-md bg-black/30 px-3 py-1 text-[10px] text-zinc-600">
            {business.business_name} · Preview
          </div>
        </div>

        <div className="flex min-h-[650px] justify-center overflow-auto bg-[#252529] p-3 sm:p-6">
          <div
            className={`overflow-hidden bg-white shadow-2xl transition-all duration-300 ${
              view === "mobile"
                ? "w-[390px] max-w-full rounded-2xl border-[5px] border-zinc-800"
                : "w-full rounded-md"
            }`}
          >
            <iframe
              key={refreshKey}
              src={previewUrl}
              title={`${business.business_name} website preview`}
              sandbox="allow-scripts"
              referrerPolicy="no-referrer"
              className="block w-full border-0 bg-white"
              style={{
                height: "min(75vh, 850px)",
                minHeight: "620px",
              }}
            />
          </div>
        </div>
      </div>

      <p className="text-[11px] leading-5 text-zinc-600">
        This is a local development preview. Changes to the generated files
        will appear after refreshing the preview.
      </p>
    </section>
  );
}

function SettingsPage({
  backend,
}: {
  backend: "checking" | "connected" | "offline";
}) {
  return (
    <section className="max-w-2xl space-y-7">
      <div>
        <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-lime-300">
          Configuration
        </p>
        <h2 className="text-3xl font-semibold tracking-tight">
          Application settings
        </h2>
        <p className="mt-2 text-sm text-zinc-500">
          Current development environment and service status.
        </p>
      </div>

      <div className="rounded-xl border border-white/[0.08] bg-[#101014] p-5">
        <div className="mb-5 flex items-center gap-2">
          <Activity size={17} className="text-lime-300" />
          <h3 className="text-sm font-semibold">Backend connection</h3>
        </div>

        <div className="flex items-center justify-between border-t border-white/[0.07] py-4">
          <div>
            <p className="text-sm text-zinc-300">FastAPI</p>
            <p className="mt-1 text-xs text-zinc-600">
              http://localhost:8000
            </p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs ${
              backend === "connected"
                ? "bg-lime-300/10 text-lime-300"
                : backend === "offline"
                  ? "bg-red-400/10 text-red-400"
                  : "bg-yellow-300/10 text-yellow-300"
            }`}
          >
            {backend}
          </span>
        </div>

        <div className="flex items-center justify-between border-t border-white/[0.07] py-4">
          <div>
            <p className="text-sm text-zinc-300">Frontend</p>
            <p className="mt-1 text-xs text-zinc-600">
              React + TypeScript + Vite
            </p>
          </div>
          <span className="rounded-full bg-lime-300/10 px-3 py-1 text-xs text-lime-300">
            Running
          </span>
        </div>
      </div>

      <div className="rounded-xl border border-white/[0.08] bg-[#101014] p-5">
        <h3 className="text-sm font-semibold">V1 development scope</h3>
        <p className="mt-2 text-xs leading-6 text-zinc-500">
          BizCraft V1 supports business profiles, AI-assisted business research,
          design selection, static website generation, browser preview and ZIP
          export. Hosting, payments and live site editing are outside the V1
          scope.
        </p>
      </div>
    </section>
  );
}

export default App;