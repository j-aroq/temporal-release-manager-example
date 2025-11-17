/**
 * TypeScript type definitions for release management entities.
 *
 * Defines the 5-level entity hierarchy:
 * Release → Wave → Cluster → Bundle → App
 */

export interface EntityBase {
  id: string;
  state: string;
  created_at?: string;
  updated_at?: string;
}

export interface Release extends EntityBase {
  workflow_id: string;
  wave_ids: string[];
}

export interface Wave extends EntityBase {
  release_id: string;
  sequence?: number;
  cluster_ids: string[];
}

export interface Cluster extends EntityBase {
  wave_id: string;
  name?: string;
  bundle_id?: string; // Exactly 1 bundle per cluster
}

export interface Bundle extends EntityBase {
  cluster_id: string;
  name?: string;
  app_ids: string[];
}

export interface App extends EntityBase {
  bundle_id: string;
  name?: string;
  version?: string;
}

// Aggregate types for hierarchical responses

export interface BundleWithApps {
  bundle: Bundle;
  apps: App[];
}

export interface ClusterWithBundles {
  cluster: Cluster;
  bundles: BundleWithApps[];
}

export interface WaveWithClusters {
  wave: Wave;
  clusters: ClusterWithBundles[];
}

export interface ReleaseHierarchy {
  release: Release;
  waves: WaveWithClusters[];
}

// Pagination

export interface PaginatedReleases {
  items: Release[];
  total: number;
  page: number;
  page_size: number;
}
