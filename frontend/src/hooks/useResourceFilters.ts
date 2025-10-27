'use client';

import { useState, useMemo, useCallback } from 'react';

interface FilterConfig {
  name: string;
  label: string;
  options: { label: string; value: string }[];
  filterFn: (item: any, value: string) => boolean;
}

interface UseResourceFiltersProps {
  data: any[];
  searchFields: string[];
  filterConfigs?: FilterConfig[];
}

export function useResourceFilters({
  data,
  searchFields,
  filterConfigs = [],
}: UseResourceFiltersProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterValues, setFilterValues] = useState<Record<string, string>>(
    filterConfigs.reduce((acc, config) => ({ ...acc, [config.name]: 'all' }), {})
  );

  // Filter data based on search term and filters
  const filteredData = useMemo(() => {
    let result = data;

    // Apply search filter
    if (searchTerm) {
      const lowerSearchTerm = searchTerm.toLowerCase();
      result = result.filter((item) =>
        searchFields.some((field) => {
          const value = item[field];
          if (value === null || value === undefined) return false;
          return String(value).toLowerCase().includes(lowerSearchTerm);
        })
      );
    }

    // Apply custom filters
    filterConfigs.forEach((config) => {
      const filterValue = filterValues[config.name];
      if (filterValue && filterValue !== 'all') {
        result = result.filter((item) => config.filterFn(item, filterValue));
      }
    });

    return result;
  }, [data, searchTerm, filterValues, searchFields, filterConfigs]);

  // Update a specific filter
  const updateFilter = useCallback((name: string, value: string) => {
    setFilterValues((prev) => ({ ...prev, [name]: value }));
  }, []);

  // Clear all filters
  const clearAllFilters = useCallback(() => {
    setSearchTerm('');
    setFilterValues(
      filterConfigs.reduce((acc, config) => ({ ...acc, [config.name]: 'all' }), {})
    );
  }, [filterConfigs]);

  // Check if any filters are active
  const hasActiveFilters = useMemo(() => {
    return (
      searchTerm !== '' ||
      Object.values(filterValues).some((value) => value !== 'all')
    );
  }, [searchTerm, filterValues]);

  return {
    searchTerm,
    setSearchTerm,
    filterValues,
    updateFilter,
    filteredData,
    clearAllFilters,
    hasActiveFilters,
    resultCount: filteredData.length,
    totalCount: data.length,
  };
}