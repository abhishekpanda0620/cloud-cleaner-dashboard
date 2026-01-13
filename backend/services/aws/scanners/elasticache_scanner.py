"""
Elasticache Scanner for identifying unused Cache clusters.

This scanner checks for Elasticache clusters that are:
- Available but with no connections
- Available but with very low cache activity
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..scanner_base import ScannerBase

logger = logging.getLogger(__name__)


class ElasticacheScanner(ScannerBase):
    """
    Scanner for Amazon ElastiCache clusters.
    
    Identifies unused clusters based on:
    - Current connections (< 1 for 7+ days)
    - Cache hits/misses (very low activity for 7+ days)
    """
    
    @property
    def service_name(self) -> str:
        return "Amazon ElastiCache"
    
    @property
    def service_code(self) -> str:
        return "AmazonElastiCache"
    
    @property
    def service_category(self) -> str:
        return "Database"
    
    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan for Elasticache clusters across regions.
        """
        if regions is None:
            regions = self.get_supported_regions()
        
        all_clusters = []
        
        for region in regions:
            try:
                clusters = self._scan_region(region)
                all_clusters.extend(clusters)
                logger.info(f"Found {len(clusters)} Elasticache clusters in {region}")
            except Exception as e:
                logger.error(f"Error scanning Elasticache in {region}: {e}")
                continue
        
        return all_clusters
    
    def _scan_region(self, region: str) -> List[Dict[str, Any]]:
        """
        Scan Elasticache clusters in a specific region.
        """
        clusters = []
        
        try:
            client = self.session.client('elasticache', region_name=region)
            
            # Describe all cache clusters
            paginator = client.get_paginator('describe_cache_clusters')
            page_iterator = paginator.paginate(ShowCacheNodeInfo=True)
            
            for page in page_iterator:
                for cluster in page['CacheClusters']:
                    resource = self._process_cluster(cluster, region)
                    clusters.append(resource)
        
        except Exception as e:
            logger.error(f"Error describing Elasticache clusters in {region}: {e}")
            raise
        
        return clusters
    
    def _process_cluster(self, cluster: Dict[str, Any], region: str) -> Dict[str, Any]:
        """
        Process an Elasticache cluster into standardized resource format.
        """
        cluster_id = cluster['CacheClusterId']
        node_type = cluster['CacheNodeType']
        engine = cluster['Engine']
        status = cluster['CacheClusterStatus']
        num_nodes = cluster.get('NumCacheNodes', 1)
        
        # Determine if unused
        is_unused = self.identify_unused(cluster)
        
        # Estimate monthly cost
        monthly_cost = self.estimate_monthly_cost(node_type, cluster)
        
        return {
            'resource_id': cluster_id,
            'resource_type': 'ElasticacheCluster',
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'cluster_id': cluster_id,
                'node_type': node_type,
                'engine': engine,
                'engine_version': cluster.get('EngineVersion'),
                'status': status,
                'num_nodes': num_nodes,
                'preferred_az': cluster.get('PreferredAvailabilityZone'),
                'endpoint': cluster.get('ConfigurationEndpoint', {}).get('Address'),
                'port': cluster.get('ConfigurationEndpoint', {}).get('Port'),
            },
            'tags': {}, # Elasticache tags need separate API call usually, skip for now or implement if needed
            'last_seen': datetime.utcnow()
        }
    
    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        """
        Determine if an Elasticache cluster is unused.
        """
        # Handle both raw boto3 format and standardized format
        if 'CacheClusterStatus' in resource:
            # Raw boto3 format
            status = resource['CacheClusterStatus']
            cluster_id = resource['CacheClusterId']
            # Region is tricky if passed raw, typically we are in a region context
            # For this simple implementation we rely on the caller context or default region if not available, 
            # but ideally we pass region. However, identify_unused signature is fixed.
            # In ScannerBase, identify_unused receives the standardized resource dict usually after scan.
            # But here `_process_cluster` calls it with raw dict.
            # Let's check `_process_cluster`. It calls it with `cluster` (raw).
            # We need region to make CloudWatch calls. 
            # Since `identify_unused` abstract method signature only has `resource`, 
            # we should update `_process_cluster` to pass a dict that has region, or 
            # we should look at how we implemented it in RDS.
            # In RDS `identify_unused` it handles both. But for region it guesses or defaults.
            # Let's rely on self.region or 'us-east-1' if scanned via `scan`. 
            # BUT scan iterates regions. self.region might be the init region which is default us-east-1.
            # Correct approach: `_process_cluster` has `region`.
            # Let's stick to standardized approach: `identify_unused` is best called on the standardized resource.
            # However, to be efficient, we want to know 'unused' status BEFORE creating the final dict? 
            # No, we can create the dict first with unused=False, then update it.
            # Or just accept that we might not have perfect region access if called raw without context.
            pass
        else:
             # Standardized format
            status = resource.get('resource_config', {}).get('status', 'unknown')
            cluster_id = resource.get('resource_id')
        
        # Check failed/deleting states
        if status in ['create-failed', 'deleting', 'deleted', 'incompatible-network']:
            return True
            
        if status == 'available':
            # We need region for CW calls. In standardized it is there.
            # If called from `_process_cluster`, we have a problem.
            # Let's fix `_process_cluster` to call `_check_low_utilization` directly instead of `identify_unused`
            # or pass region in a way `identify_unused` can use if we want to stick to the interface.
            return False # Post-process or handle loop. 
            
        return False
    
    # Overriding to allow passing region explicitly for internal use or use standardized resource
    def identify_unused_with_region(self, resource: Dict[str, Any], region: str) -> bool:
        status = resource.get('CacheClusterStatus', resource.get('resource_config', {}).get('status'))
        cluster_id = resource.get('CacheClusterId', resource.get('resource_id'))
        
        if status in ['create-failed', 'deleting', 'deleted']:
            return True
            
        if status == 'available':
            return self._check_low_utilization(cluster_id, region)
            
        return False

    def _process_cluster(self, cluster: Dict[str, Any], region: str) -> Dict[str, Any]:
        # ... logic repeated ...
        cluster_id = cluster['CacheClusterId']
        is_unused = self.identify_unused_with_region(cluster, region)
        # ...
        return self._create_standardized_resource(cluster, region, is_unused)

    def _create_standardized_resource(self, cluster, region, is_unused):
        # helper to avoid code duplication if I rewrote above
        cluster_id = cluster['CacheClusterId']
        node_type = cluster['CacheNodeType']
        # ... same as above ...
        monthly_cost = self.estimate_monthly_cost(node_type, cluster)
        return {
            'resource_id': cluster_id,
            'resource_type': 'ElasticacheCluster',
            'region': region,
            'status': 'unused' if is_unused else 'active',
            'estimated_monthly_cost': monthly_cost,
             'resource_config': {
                'cluster_id': cluster_id,
                'node_type': node_type,
                'engine': cluster['Engine'],
                'engine_version': cluster.get('EngineVersion'),
                'status': cluster['CacheClusterStatus'],
                'num_nodes': cluster.get('NumCacheNodes', 1),
                'endpoint': cluster.get('ConfigurationEndpoint', {}).get('Address'),
            },
            'tags': {},
            'last_seen': datetime.utcnow()
        }
        
    def _check_low_utilization(self, cluster_id: str, region: str) -> bool:
        """
        Check if Elasticache cluster has low utilization based on CloudWatch metrics.
        """
        try:
            # Check Connections
            conn_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/ElastiCache',
                metric_name='CurrConnections',
                dimensions=[{'Name': 'CacheClusterId', 'Value': cluster_id}],
                days=7
            )
            
            if conn_metrics:
                avg_conn = sum(m.get('Average', 0) for m in conn_metrics) / len(conn_metrics)
                if avg_conn < 1.0:
                    logger.debug(f"Elasticache {cluster_id} has low connections: {avg_conn:.2f}")
                    return True
            
            # Check Cache Hits/Misses (Activity)
            # If both are near zero, it's unused
            hits_metrics = self.get_cloudwatch_metrics(
                namespace='AWS/ElastiCache',
                metric_name='CacheHits',
                dimensions=[{'Name': 'CacheClusterId', 'Value': cluster_id}],
                days=7
            )
            
            if hits_metrics:
                avg_hits = sum(m.get('Average', 0) for m in hits_metrics) / len(hits_metrics)
                # We can also check misses
                # Simplified: if hits are very low, it's virtually unused.
                if avg_hits < 5.0: 
                    logger.debug(f"Elasticache {cluster_id} has low hits: {avg_hits:.2f}")
                    return True

        except Exception as e:
            logger.warning(f"Could not check utilization for {cluster_id}: {e}")
            
        return False
        
    def estimate_monthly_cost(self, resource_type: str, resource_config: Dict[str, Any]) -> float:
        # Simplified pricing
        engine = resource_config.get('engine', 'redis')
        hourly_rate = self.pricing_service.get_elasticache_price(resource_type, self.region, engine)
        
        if hourly_rate == 0.0:
            # Simplified pricing
            pricing = {
                'cache.t2.micro': 0.017,
                'cache.t2.small': 0.034,
                'cache.t2.medium': 0.068,
                'cache.t3.micro': 0.017,
                'cache.t3.small': 0.034,
                'cache.t3.medium': 0.068,
                'cache.m4.large': 0.156,
                'cache.m4.xlarge': 0.312,
                'cache.r4.large': 0.25,
                'cache.r4.xlarge': 0.50,
            }
            hourly_rate = pricing.get(resource_type, 0.10)
        num_nodes = resource_config.get('NumCacheNodes', 1)
        if isinstance(resource_config, dict) and 'num_nodes' in resource_config:
             num_nodes = resource_config['num_nodes']
             
        # cache.t2.micro etc price is per node
        monthly_cost = hourly_rate * 730 * num_nodes
        return round(monthly_cost, 2)
