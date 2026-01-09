'use client';

import { useState, useMemo, useCallback } from 'react';

interface FilterConfig<T> {
  name: string;
  label: string;
  options: { label: string; value: string }[];
  filterFn: (item: T, value: string) => boolean;
}

interface UseResourceFiltersProps<T> {
  data: T[];
  searchFields: (keyof T | string)[];
  filterConfigs?: FilterConfig<T>[];
}

export function useResourceFilters<T>({
  data,
  searchFields,
  filterConfigs = [],
}: UseResourceFiltersProps<T>) {
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
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const value = (item as any)[field];
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
  }, [filterConfigs, setSearchTerm, setFilterValues]);

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