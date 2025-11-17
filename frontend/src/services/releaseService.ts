/**
 * Release service for fetching release data from API.
 *
 * Provides methods to list releases and get release details.
 */

import apiClient from './api';
import { Release, PaginatedReleases, ReleaseHierarchy } from '../types/entities';

class ReleaseService {
  /**
   * List releases with pagination.
   *
   * @param page - Page number (1-indexed)
   * @param pageSize - Number of releases per page
   * @returns Paginated list of releases
   */
  async listReleases(page: number = 1, pageSize: number = 20): Promise<PaginatedReleases> {
    const response = await apiClient.get<PaginatedReleases>('/releases', {
      params: {
        page,
        page_size: pageSize,
      },
    });

    return response.data;
  }

  /**
   * Get single release by ID.
   *
   * @param releaseId - Release ID (format: release:id)
   * @returns Release details
   */
  async getRelease(releaseId: string): Promise<Release> {
    const response = await apiClient.get<Release>(`/releases/${releaseId}`);
    return response.data;
  }

  /**
   * Get release hierarchy (full tree of entities).
   *
   * @param releaseId - Release ID (format: release:id)
   * @returns Complete release hierarchy
   */
  async getReleaseHierarchy(releaseId: string): Promise<ReleaseHierarchy> {
    const response = await apiClient.get<ReleaseHierarchy>(
      `/releases/${releaseId}/hierarchy`
    );
    return response.data;
  }
}

// Export singleton instance
const releaseService = new ReleaseService();
export default releaseService;
