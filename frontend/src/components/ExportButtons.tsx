/**
 * Export functionality for release data.
 *
 * Provides CSV and JSON export options.
 */

import React from 'react';
import { Button, HStack, Icon, useToast } from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';
import { Release } from '../types/entities';

interface ExportButtonsProps {
  releases: Release[];
  filename?: string;
}

export const ExportButtons: React.FC<ExportButtonsProps> = ({
  releases,
  filename = 'releases',
}) => {
  const toast = useToast();

  const exportToCSV = () => {
    try {
      // Create CSV header
      const headers = ['Release ID', 'State', 'Workflow ID', 'Waves', 'Updated'];
      const csvRows = [headers.join(',')];

      // Add data rows
      releases.forEach((release) => {
        const row = [
          release.id,
          release.state,
          release.workflow_id,
          release.wave_ids.length.toString(),
          release.updated_at || '',
        ];
        csvRows.push(row.join(','));
      });

      // Create blob and download
      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${filename}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast({
        title: 'Export successful',
        description: `Exported ${releases.length} releases to CSV`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: 'Failed to export releases to CSV',
        status: 'error',
        duration: 5000,
      });
    }
  };

  const exportToJSON = () => {
    try {
      const jsonContent = JSON.stringify(releases, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${filename}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast({
        title: 'Export successful',
        description: `Exported ${releases.length} releases to JSON`,
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: 'Failed to export releases to JSON',
        status: 'error',
        duration: 5000,
      });
    }
  };

  return (
    <HStack spacing={2}>
      <Button
        size="sm"
        variant="outline"
        leftIcon={<Icon as={DownloadIcon} />}
        onClick={exportToCSV}
        isDisabled={releases.length === 0}
        aria-label="Export to CSV"
      >
        Export CSV
      </Button>
      <Button
        size="sm"
        variant="outline"
        leftIcon={<Icon as={DownloadIcon} />}
        onClick={exportToJSON}
        isDisabled={releases.length === 0}
        aria-label="Export to JSON"
      >
        Export JSON
      </Button>
    </HStack>
  );
};
