"use client";

import React from "react";
import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import {
  CircleAlert,
  GitBranch,
  Github,
  RefreshCw,
  Settings,
  Star,
  Trash2,
} from "lucide-react";

import {
  getRegisteredRepositories,
  refreshRegisteredRepository,
  type RegisteredRepository,
  unregisterRegisteredRepository,
  updateRegisteredRepositorySettings,
} from "../../api/github";
import { useAuth } from "../../features/auth/auth-hooks";
import { RequireAuth } from "../../features/auth/require-auth";

type RepositorySettingsForm = {
  displayName: string;
  favorite: boolean;
  notes: string;
};

function RegisteredRepositorySkeletons() {
  return (
    <div className="grid gap-3" aria-label="Loading registered repositories">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="h-4 w-2/5 animate-pulse rounded bg-muted" />
              <div className="mt-2 h-3 w-1/4 animate-pulse rounded bg-muted" />
            </div>
            <div className="h-6 w-24 animate-pulse rounded-full bg-muted" />
          </div>
          <div className="mt-4 h-3 w-full animate-pulse rounded bg-muted" />
          <div className="mt-2 h-3 w-2/3 animate-pulse rounded bg-muted" />
        </div>
      ))}
    </div>
  );
}

function formatDate(value: string | null) {
  if (!value) {
    return "Not synchronized yet";
  }

  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function getSyncStatusClass(status: RegisteredRepository["sync_status"]) {
  if (status === "READY") {
    return "border-primary/30 bg-primary/10 text-primary";
  }

  if (status === "ERROR") {
    return "border-destructive/40 bg-destructive/10 text-destructive";
  }

  return "border-border bg-secondary text-secondary-foreground";
}

type RegisteredRepositoryCardProps = {
  actionError: string | null;
  confirmRepositoryId: string | null;
  editingRepositoryId: string | null;
  form: RepositorySettingsForm;
  onCancelDelete: () => void;
  onCancelSettings: () => void;
  onConfirmDelete: (repository: RegisteredRepository) => void;
  onDeleteClick: (repositoryId: string) => void;
  onFormChange: (form: RepositorySettingsForm) => void;
  onRefresh: (repository: RegisteredRepository) => void;
  onSaveSettings: (repository: RegisteredRepository, event: FormEvent<HTMLFormElement>) => void;
  onSettingsClick: (repository: RegisteredRepository) => void;
  onToggleFavorite: (repository: RegisteredRepository) => void;
  pendingAction: string | null;
  repository: RegisteredRepository;
};

function RegisteredRepositoryCard({
  actionError,
  confirmRepositoryId,
  editingRepositoryId,
  form,
  onCancelDelete,
  onCancelSettings,
  onConfirmDelete,
  onDeleteClick,
  onFormChange,
  onRefresh,
  onSaveSettings,
  onSettingsClick,
  onToggleFavorite,
  pendingAction,
  repository,
}: RegisteredRepositoryCardProps) {
  const title = repository.display_name || repository.name;
  const isPending = pendingAction?.startsWith(repository.id);
  const isEditing = editingRepositoryId === repository.id;
  const isConfirmingDelete = confirmRepositoryId === repository.id;

  return (
    <article className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="truncate text-base font-semibold text-card-foreground">{title}</h2>
            {repository.favorite ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                <Star aria-hidden="true" className="h-3.5 w-3.5 fill-current" />
                Favorite
              </span>
            ) : null}
          </div>
          <p className="mt-1 truncate text-sm text-muted-foreground">{repository.full_name}</p>
        </div>
        <span
          className={`inline-flex w-fit rounded-full border px-2 py-1 text-xs font-medium ${getSyncStatusClass(
            repository.sync_status,
          )}`}
        >
          {repository.sync_status}
        </span>
      </div>

      <p className="mt-4 text-sm text-muted-foreground">
        {repository.notes || repository.description || "No description provided for this repository."}
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span className="rounded-md border border-border bg-background px-2 py-1 font-medium text-foreground">
          {repository.language ?? "Unknown language"}
        </span>
        <span className="inline-flex items-center gap-1 rounded-md border border-border bg-background px-2 py-1">
          <GitBranch aria-hidden="true" className="h-3 w-3" />
          {repository.default_branch}
        </span>
        <span className="rounded-md border border-border bg-background px-2 py-1 capitalize">
          {repository.visibility}
        </span>
        <span className="rounded-md border border-border bg-background px-2 py-1">
          Last synchronized {formatDate(repository.last_synced_at)}
        </span>
      </div>

      {isEditing ? (
        <form
          className="mt-5 rounded-md border border-border bg-background p-4"
          onSubmit={(event) => onSaveSettings(repository, event)}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="grid gap-1 text-sm font-medium text-foreground">
              Alias
              <input
                value={form.displayName}
                onChange={(event) => onFormChange({ ...form, displayName: event.target.value })}
                maxLength={255}
                className="h-10 rounded-md border border-border bg-card px-3 text-sm font-normal outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                placeholder="Optional display name"
              />
            </label>
            <label className="flex items-center gap-2 self-end text-sm font-medium text-foreground">
              <input
                type="checkbox"
                checked={form.favorite}
                onChange={(event) => onFormChange({ ...form, favorite: event.target.checked })}
                className="h-4 w-4 rounded border-border"
              />
              Favorite repository
            </label>
          </div>
          <label className="mt-3 grid gap-1 text-sm font-medium text-foreground">
            Notes
            <textarea
              value={form.notes}
              onChange={(event) => onFormChange({ ...form, notes: event.target.value })}
              maxLength={1000}
              rows={3}
              className="rounded-md border border-border bg-card px-3 py-2 text-sm font-normal outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              placeholder="Short private note"
            />
          </label>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={isPending}
              className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Save Settings
            </button>
            <button
              type="button"
              onClick={onCancelSettings}
              className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}

      {isConfirmingDelete ? (
        <div
          role="alertdialog"
          aria-label={`Unregister ${repository.full_name}`}
          className="mt-5 rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm"
        >
          <p className="font-medium text-destructive">Unregister this repository?</p>
          <p className="mt-2 text-muted-foreground">
            This removes it from RepoMind AI only. The GitHub repository will not be deleted.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={isPending}
              onClick={() => onConfirmDelete(repository)}
              className="inline-flex h-9 items-center justify-center rounded-md bg-destructive px-3 text-sm font-medium text-destructive-foreground outline-none transition-colors hover:bg-destructive/90 focus:ring-2 focus:ring-destructive/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Confirm Unregister
            </button>
            <button
              type="button"
              onClick={onCancelDelete}
              className="inline-flex h-9 items-center justify-center rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : null}

      {actionError ? (
        <p role="alert" className="mt-4 text-sm text-destructive">
          {actionError}
        </p>
      ) : null}

      <div className="mt-5 flex flex-wrap justify-end gap-2 border-t border-border pt-4">
        <button
          type="button"
          disabled={isPending}
          onClick={() => onToggleFavorite(repository)}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Star aria-hidden="true" className={repository.favorite ? "h-4 w-4 fill-current" : "h-4 w-4"} />
          {repository.favorite ? "Unfavorite" : "Favorite"}
        </button>
        <button
          type="button"
          disabled={isPending}
          onClick={() => onRefresh(repository)}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw aria-hidden="true" className="h-4 w-4" />
          Refresh
        </button>
        <button
          type="button"
          onClick={() => onSettingsClick(repository)}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-primary/20"
        >
          <Settings aria-hidden="true" className="h-4 w-4" />
          Settings
        </button>
        <button
          type="button"
          onClick={() => onDeleteClick(repository.id)}
          className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-destructive/40 bg-background px-3 text-sm font-medium text-destructive outline-none transition-colors hover:bg-destructive/10 focus:ring-2 focus:ring-destructive/30"
        >
          <Trash2 aria-hidden="true" className="h-4 w-4" />
          Unregister
        </button>
        <Link
          href={`/repositories/${repository.id}`}
          className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground outline-none transition-colors hover:bg-primary/90 focus:ring-2 focus:ring-primary/30"
        >
          Open Dashboard
        </Link>
      </div>
    </article>
  );
}

function RepositoriesContent() {
  const { session } = useAuth();
  const [repositories, setRepositories] = useState<RegisteredRepository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<Record<string, string>>({});
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [editingRepositoryId, setEditingRepositoryId] = useState<string | null>(null);
  const [confirmRepositoryId, setConfirmRepositoryId] = useState<string | null>(null);
  const [form, setForm] = useState<RepositorySettingsForm>({
    displayName: "",
    favorite: false,
    notes: "",
  });
  const [retryAttempt, setRetryAttempt] = useState(0);

  function replaceRepository(nextRepository: RegisteredRepository) {
    setRepositories((currentRepositories) =>
      currentRepositories.map((repository) =>
        repository.id === nextRepository.id ? nextRepository : repository,
      ),
    );
  }

  useEffect(() => {
    if (!session) {
      return;
    }

    let isMounted = true;
    async function loadRepositories() {
      setLoading(true);
      setError(null);
      try {
        const result = await getRegisteredRepositories({ getSession: async () => session });
        if (isMounted) {
          setRepositories(result);
        }
      } catch {
        if (isMounted) {
          setRepositories([]);
          setError("Registered repositories could not be loaded. Please retry.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    void loadRepositories();

    return () => {
      isMounted = false;
    };
  }, [retryAttempt, session]);

  async function handleRefresh(repository: RegisteredRepository) {
    if (!session) {
      return;
    }
    setPendingAction(`${repository.id}:refresh`);
    setActionError((currentErrors) => ({ ...currentErrors, [repository.id]: "" }));
    try {
      const refreshedRepository = await refreshRegisteredRepository(
        { getSession: async () => session },
        repository.id,
      );
      replaceRepository(refreshedRepository);
    } catch {
      setActionError((currentErrors) => ({
        ...currentErrors,
        [repository.id]: "Repository metadata could not be refreshed. Please retry.",
      }));
    } finally {
      setPendingAction(null);
    }
  }

  async function handleToggleFavorite(repository: RegisteredRepository) {
    if (!session) {
      return;
    }
    setPendingAction(`${repository.id}:favorite`);
    setActionError((currentErrors) => ({ ...currentErrors, [repository.id]: "" }));
    try {
      const updatedRepository = await updateRegisteredRepositorySettings(
        { getSession: async () => session },
        repository.id,
        { favorite: !repository.favorite },
      );
      replaceRepository(updatedRepository);
    } catch {
      setActionError((currentErrors) => ({
        ...currentErrors,
        [repository.id]: "Favorite status could not be updated. Please retry.",
      }));
    } finally {
      setPendingAction(null);
    }
  }

  function handleSettingsClick(repository: RegisteredRepository) {
    setConfirmRepositoryId(null);
    setEditingRepositoryId(repository.id);
    setForm({
      displayName: repository.display_name ?? "",
      favorite: repository.favorite,
      notes: repository.notes ?? "",
    });
  }

  async function handleSaveSettings(
    repository: RegisteredRepository,
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    if (!session) {
      return;
    }
    setPendingAction(`${repository.id}:settings`);
    setActionError((currentErrors) => ({ ...currentErrors, [repository.id]: "" }));
    try {
      const updatedRepository = await updateRegisteredRepositorySettings(
        { getSession: async () => session },
        repository.id,
        {
          display_name: form.displayName.trim() || null,
          favorite: form.favorite,
          notes: form.notes.trim() || null,
        },
      );
      replaceRepository(updatedRepository);
      setEditingRepositoryId(null);
    } catch {
      setActionError((currentErrors) => ({
        ...currentErrors,
        [repository.id]: "Repository settings could not be saved. Please retry.",
      }));
    } finally {
      setPendingAction(null);
    }
  }

  async function handleConfirmDelete(repository: RegisteredRepository) {
    if (!session) {
      return;
    }
    setPendingAction(`${repository.id}:delete`);
    setActionError((currentErrors) => ({ ...currentErrors, [repository.id]: "" }));
    try {
      await unregisterRegisteredRepository({ getSession: async () => session }, repository.id);
      setRepositories((currentRepositories) =>
        currentRepositories.filter((currentRepository) => currentRepository.id !== repository.id),
      );
      setConfirmRepositoryId(null);
    } catch {
      setActionError((currentErrors) => ({
        ...currentErrors,
        [repository.id]: "Repository could not be unregistered. Please retry.",
      }));
    } finally {
      setPendingAction(null);
    }
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6 sm:py-10">
      <section className="mx-auto max-w-4xl">
        <div className="flex flex-col gap-4 border-b border-border pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-medium uppercase text-muted-foreground">My Repositories</p>
            <h1 className="mt-3 text-3xl font-semibold">Registered repositories</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Managed repositories registered from your linked GitHub account.
            </p>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex h-10 w-fit items-center justify-center rounded-md border border-border bg-background px-4 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
          >
            Browse GitHub repositories
          </Link>
        </div>

        <div className="mt-6" aria-live="polite" aria-busy={loading}>
          {loading ? <RegisteredRepositorySkeletons /> : null}

          {!loading && error ? (
            <div
              role="alert"
              className="rounded-md border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive"
            >
              <p className="inline-flex items-center gap-2">
                <CircleAlert aria-hidden="true" className="h-4 w-4" />
                {error}
              </p>
              <button
                type="button"
                onClick={() => setRetryAttempt((currentAttempt) => currentAttempt + 1)}
                className="mt-3 inline-flex h-9 items-center justify-center gap-2 rounded-md border border-destructive/40 bg-background px-3 text-sm font-medium text-foreground outline-none transition-colors hover:bg-secondary focus:ring-2 focus:ring-destructive/30"
              >
                <RefreshCw aria-hidden="true" className="h-4 w-4" />
                Retry
              </button>
            </div>
          ) : null}

          {!loading && !error && repositories.length > 0 ? (
            <div className="grid gap-3">
              {repositories.map((repository) => (
                <RegisteredRepositoryCard
                  key={repository.id}
                  actionError={actionError[repository.id] || null}
                  confirmRepositoryId={confirmRepositoryId}
                  editingRepositoryId={editingRepositoryId}
                  form={form}
                  onCancelDelete={() => setConfirmRepositoryId(null)}
                  onCancelSettings={() => setEditingRepositoryId(null)}
                  onConfirmDelete={handleConfirmDelete}
                  onDeleteClick={(repositoryId) => {
                    setEditingRepositoryId(null);
                    setConfirmRepositoryId(repositoryId);
                  }}
                  onFormChange={setForm}
                  onRefresh={handleRefresh}
                  onSaveSettings={handleSaveSettings}
                  onSettingsClick={handleSettingsClick}
                  onToggleFavorite={handleToggleFavorite}
                  pendingAction={pendingAction}
                  repository={repository}
                />
              ))}
            </div>
          ) : null}

          {!loading && !error && repositories.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center shadow-sm">
              <Github aria-hidden="true" className="mx-auto h-8 w-8 text-muted-foreground" />
              <h2 className="mt-4 text-base font-semibold text-card-foreground">
                No registered repositories yet
              </h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                Register repositories from the dashboard to make them managed RepoMind AI resources.
              </p>
            </div>
          ) : null}
        </div>
      </section>
    </main>
  );
}

export default function RepositoriesPage() {
  return (
    <RequireAuth>
      <RepositoriesContent />
    </RequireAuth>
  );
}