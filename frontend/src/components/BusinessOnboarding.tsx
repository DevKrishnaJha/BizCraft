
import { useState, type FormEvent } from "react";

import {
  ArrowLeft,
  ArrowRight,
  Building2,
  CheckCircle2,
  Globe2,
  LoaderCircle,
  MapPin,
  Plus,
  Search,
  Sparkles,
} from "lucide-react";


interface BusinessOnboardingProps {
  onBack: () => void;
  onSaved: () => void;
}

interface BusinessForm {
  business_name: string;
  category: string;
  location: string;
  phone: string;
  email: string;
  website: string;
  google_maps_url: string;
  description: string;
  services: string;
  opening_hours: string;
}

interface AutofillResponse {
  status: "success" | "no_match" | "ambiguous";
  message?: string;
  business?: {
    business_name: string | null;
    category: string | null;
    location: string | null;
    phone: string | null;
    email: string | null;
    website: string | null;
    google_maps_url: string | null;
    description: string | null;
    services: string[];
    opening_hours: string | null;
  };
  missing_fields?: string[];
}

const initialForm: BusinessForm = {
  business_name: "",
  category: "",
  location: "",
  phone: "",
  email: "",
  website: "",
  google_maps_url: "",
  description: "",
  services: "",
  opening_hours: "",
};

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function BusinessOnboarding({
  onBack,
  onSaved,
}: BusinessOnboardingProps) {

  const [form, setForm] = useState<BusinessForm>(initialForm);

  const [loading, setLoading] = useState(false);
  const [lookupLoading, setLookupLoading] = useState(false);

  const [error, setError] = useState("");
  const [lookupError, setLookupError] = useState("");
  const [lookupMessage, setLookupMessage] = useState("");

  const [saved, setSaved] = useState(false);
  const [savedName, setSavedName] = useState("");


  // --------------------------------------------------
  // Form updates
  // --------------------------------------------------

  function updateField(
    field: keyof BusinessForm,
    value: string,
  ) {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));

    if (field === "google_maps_url") {
      setLookupError("");
      setLookupMessage("");
    }
  }


  // --------------------------------------------------
  // AI business autofill
  // --------------------------------------------------

  async function handleLookup() {
    const mapsUrl = form.google_maps_url.trim();

    if (!mapsUrl) {
      setLookupError("Paste a Google Maps link first.");
      return;
    }

    setLookupLoading(true);
    setLookupError("");
    setLookupMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/businesses/autofill`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            maps_url: mapsUrl,
          }),
        },
      );

      const data: AutofillResponse = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message ||
          (typeof (data as any).detail === "string"
            ? (data as any).detail
            : "Unable to retrieve business information."),
        );
      }

      if (data.status !== "success" || !data.business) {
        setLookupMessage(
          data.message ||
          "We couldn't confidently identify this business. Check the link or enter the information manually.",
        );

        return;
      }

      const business = data.business;

      setForm((previous) => ({
        ...previous,

        business_name:
          business.business_name || "",

        category:
          business.category || "",

        location:
          business.location || "",

        phone:
          business.phone || "",

        email:
          business.email || "",

        website:
          business.website || "",

        google_maps_url:
          mapsUrl,

        description:
          business.description || "",

        services:
          Array.isArray(business.services)
            ? business.services.join(", ")
            : "",

        opening_hours:
          business.opening_hours || "",
      }));

      const missing = data.missing_fields || [];

      if (missing.length > 0) {
        setLookupMessage(
          `Business identified! Some information is unavailable: ${missing.join(", ")}. Please complete and verify these fields.`,
        );
      } else {
        setLookupMessage(
          "Business information retrieved successfully. Please review the details before saving.",
        );
      }

    } catch (err) {
      setLookupError(
        err instanceof Error
          ? err.message
          : "Something went wrong during business research.",
      );

    } finally {
      setLookupLoading(false);
    }
  }


  // --------------------------------------------------
  // Save business
  // --------------------------------------------------

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError("");

    const payload = {
      ...form,

      services: form.services
        .split(",")
        .map((service) => service.trim())
        .filter(Boolean),

      phone: form.phone || null,
      email: form.email || null,
      website: form.website || null,
      google_maps_url: form.google_maps_url || null,
      description: form.description || null,
      opening_hours: form.opening_hours || null,
    };

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/businesses/autofill`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        const detail = data.detail;

        if (Array.isArray(detail)) {
          throw new Error(
            detail
              .map((item: { msg: string }) => item.msg)
              .join(", "),
          );
        }

        throw new Error(
          typeof detail === "string"
            ? detail
            : "Unable to save business information.",
        );
      }

      setSavedName(data.business_name);
      setSaved(true);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again.",
      );

    } finally {
      setLoading(false);
    }
  }


  // --------------------------------------------------
  // Styling
  // --------------------------------------------------

  const inputClass =
    "mt-2 w-full rounded-lg border border-white/10 bg-[#101014] px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-lime-300/60";

  const labelClass =
    "text-xs font-medium text-zinc-400";


  // --------------------------------------------------
  // Saved screen
  // --------------------------------------------------

  if (saved) {
    return (
      <div className="mx-auto max-w-xl py-16 text-center">

        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-lime-300/20 bg-lime-300/10 text-lime-300">
          <CheckCircle2 size={32} />
        </div>

        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-lime-300">
          Information saved
        </p>

        <h2 className="text-3xl font-semibold tracking-tight">
          Business added successfully.
        </h2>

        <p className="mt-3 text-sm text-zinc-500">
          <span className="text-zinc-200">
            {savedName}
          </span>{" "}
          has been saved to your BizCraft workspace.
        </p>

        <button
          onClick={onSaved}
          className="mt-8 inline-flex items-center gap-2 rounded-lg bg-lime-300 px-5 py-3 text-sm font-semibold text-black transition hover:bg-lime-200"
        >
          View businesses
          <ArrowRight size={17} />
        </button>

      </div>
    );
  }


  // --------------------------------------------------
  // Main onboarding form
  // --------------------------------------------------

  return (
    <div className="mx-auto max-w-4xl space-y-8 pb-10">

      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-zinc-500 transition hover:text-white"
      >
        <ArrowLeft size={16} />
        Back to dashboard
      </button>


      {/* Heading */}

      <div>

        <div className="mb-3 flex items-center gap-2">
          <Sparkles
            size={15}
            className="text-lime-300"
          />

          <span className="text-[11px] font-semibold uppercase tracking-[0.2em] text-lime-300">
            New website project
          </span>
        </div>

        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Tell us about your business.
        </h2>

        <p className="mt-3 max-w-xl text-sm leading-6 text-zinc-500">
          Paste your Google Maps link and let BizCraft
          research and organise the available business
          information automatically.
        </p>

      </div>


      <form
        onSubmit={handleSubmit}
        className="space-y-6"
      >

        {/* ------------------------------------------ */}
        {/* AI Business Research */}
        {/* ------------------------------------------ */}

        <section className="rounded-xl border border-lime-300/20 bg-[#101014] p-5 sm:p-7">

          <div className="mb-5 flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-lime-300/10 text-lime-300">
              <Sparkles size={20} />
            </div>

            <div>
              <h3 className="text-sm font-semibold text-white">
                AI Business Research
              </h3>

              <p className="mt-1 text-xs text-zinc-500">
                Automatically retrieve available business information
              </p>
            </div>

          </div>


          <label className={labelClass}>
            Google Maps business link

            <input
              type="url"
              maxLength={2000}
              className={inputClass}
              placeholder="Paste your Google Maps business link"
              value={form.google_maps_url}
              onChange={(event) =>
                updateField(
                  "google_maps_url",
                  event.target.value,
                )
              }
            />

          </label>


          <button
            type="button"
            onClick={handleLookup}
            disabled={
              lookupLoading ||
              !form.google_maps_url.trim()
            }
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-lime-300 px-5 py-3 text-sm font-semibold text-black transition hover:bg-lime-200 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
          >

            {lookupLoading ? (
              <>
                <LoaderCircle
                  size={17}
                  className="animate-spin"
                />

                Researching business...
              </>
            ) : (
              <>
                <Search size={17} />

                Autofill business with AI
              </>
            )}

          </button>


          <p className="mt-3 text-[11px] leading-5 text-zinc-600">
            BizCraft will retrieve available listing data
            and organise it using AI. You can review and
            edit everything before saving.
          </p>


          {lookupError && (
            <div
              role="alert"
              className="mt-4 rounded-lg border border-red-400/20 bg-red-400/10 px-4 py-3 text-xs leading-5 text-red-300"
            >
              {lookupError}
            </div>
          )}


          {lookupMessage && !lookupError && (
            <div
              role="status"
              className="mt-4 rounded-lg border border-lime-300/15 bg-lime-300/5 px-4 py-3 text-xs leading-5 text-lime-200"
            >
              {lookupMessage}
            </div>
          )}

        </section>


        {/* ------------------------------------------ */}
        {/* Business Details */}
        {/* ------------------------------------------ */}

        <section className="rounded-xl border border-white/[0.08] bg-[#101014] p-5 sm:p-7">

          <div className="mb-6 flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-lime-300/10 text-lime-300">
              <Building2 size={19} />
            </div>

            <div>
              <h3 className="text-sm font-semibold">
                Business details
              </h3>

              <p className="mt-1 text-xs text-zinc-600">
                Review and edit the retrieved information
              </p>
            </div>

          </div>


          <div className="grid gap-5 sm:grid-cols-2">

            <label className={labelClass}>
              Business name *

              <input
                required
                minLength={2}
                maxLength={120}
                className={inputClass}
                placeholder="e.g. Shree Education Hub"
                value={form.business_name}
                onChange={(event) =>
                  updateField(
                    "business_name",
                    event.target.value,
                  )
                }
              />
            </label>


            <label className={labelClass}>
              Business category *

              <input
                required
                minLength={2}
                maxLength={100}
                className={inputClass}
                placeholder="e.g. Educational Institute"
                value={form.category}
                onChange={(event) =>
                  updateField(
                    "category",
                    event.target.value,
                  )
                }
              />
            </label>


            <label className={`${labelClass} sm:col-span-2`}>
              Business location *

              <div className="relative">

                <MapPin
                  size={16}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600"
                />

                <input
                  required
                  minLength={2}
                  maxLength={200}
                  className={`${inputClass} pl-10`}
                  placeholder="City, State, Country"
                  value={form.location}
                  onChange={(event) =>
                    updateField(
                      "location",
                      event.target.value,
                    )
                  }
                />

              </div>
            </label>


            <label className={`${labelClass} sm:col-span-2`}>
              Business description

              <textarea
                maxLength={2000}
                rows={4}
                className={`${inputClass} resize-y`}
                placeholder="Describe what this business does..."
                value={form.description}
                onChange={(event) =>
                  updateField(
                    "description",
                    event.target.value,
                  )
                }
              />
            </label>

          </div>

        </section>


        {/* ------------------------------------------ */}
        {/* Contact Details */}
        {/* ------------------------------------------ */}

        <section className="rounded-xl border border-white/[0.08] bg-[#101014] p-5 sm:p-7">

          <div className="mb-6 flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-lime-300/10 text-lime-300">
              <Globe2 size={19} />
            </div>

            <div>
              <h3 className="text-sm font-semibold">
                Contact information
              </h3>

              <p className="mt-1 text-xs text-zinc-600">
                How customers can reach the business
              </p>
            </div>

          </div>


          <div className="grid gap-5 sm:grid-cols-2">

            <label className={labelClass}>
              Phone number

              <input
                type="tel"
                maxLength={30}
                className={inputClass}
                placeholder="+91 98765 43210"
                value={form.phone}
                onChange={(event) =>
                  updateField("phone", event.target.value)
                }
              />
            </label>


            <label className={labelClass}>
              Email address

              <input
                type="email"
                maxLength={254}
                className={inputClass}
                placeholder="hello@business.com"
                value={form.email}
                onChange={(event) =>
                  updateField("email", event.target.value)
                }
              />
            </label>


            <label className={`${labelClass} sm:col-span-2`}>
              Existing website

              <input
                type="url"
                maxLength={500}
                className={inputClass}
                placeholder="https://www.example.com"
                value={form.website}
                onChange={(event) =>
                  updateField("website", event.target.value)
                }
              />
            </label>

          </div>

        </section>


        {/* ------------------------------------------ */}
        {/* Services and Opening Hours */}
        {/* ------------------------------------------ */}

        <section className="rounded-xl border border-white/[0.08] bg-[#101014] p-5 sm:p-7">

          <div className="mb-6 flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-lime-300/10 text-lime-300">
              <Plus size={19} />
            </div>

            <div>
              <h3 className="text-sm font-semibold">
                Services and availability
              </h3>

              <p className="mt-1 text-xs text-zinc-600">
                What the business offers
              </p>
            </div>

          </div>


          <div className="space-y-5">

            <label className={labelClass}>
              Services offered

              <input
                className={inputClass}
                placeholder="Mathematics, Physics, Chemistry"
                value={form.services}
                onChange={(event) =>
                  updateField(
                    "services",
                    event.target.value,
                  )
                }
              />

              <span className="mt-2 block text-[11px] text-zinc-600">
                Separate individual services with commas.
              </span>
            </label>


            <label className={labelClass}>
              Opening hours

              <textarea
                maxLength={2000}
                rows={3}
                className={`${inputClass} resize-y`}
                placeholder="Monday to Saturday, 8 AM to 6 PM"
                value={form.opening_hours}
                onChange={(event) =>
                  updateField(
                    "opening_hours",
                    event.target.value,
                  )
                }
              />
            </label>

          </div>

        </section>


        {/* ------------------------------------------ */}
        {/* Errors */}
        {/* ------------------------------------------ */}

        {error && (
          <div
            role="alert"
            className="rounded-lg border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300"
          >
            {error}
          </div>
        )}


        {/* ------------------------------------------ */}
        {/* Submit */}
        {/* ------------------------------------------ */}

        <div className="flex flex-col-reverse justify-between gap-4 sm:flex-row sm:items-center">

          <p className="text-[11px] text-zinc-600">
            * Required fields
          </p>


          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-lime-300 px-6 py-3 text-sm font-semibold text-black transition hover:bg-lime-200 disabled:cursor-not-allowed disabled:opacity-60"
          >

            {loading ? (
              <>
                <LoaderCircle
                  size={17}
                  className="animate-spin"
                />

                Saving business...
              </>
            ) : (
              <>
                Save business information
                <ArrowRight size={17} />
              </>
            )}

          </button>

        </div>

      </form>

    </div>
  );
}
