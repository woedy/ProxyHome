"""
Custom renderers for proxy export functionality.

This module provides format-specific renderers for exporting proxy data
in various formats (JSON, CSV, TXT, XML, YAML) with configurable options
and proper validation.
"""

import json
import csv
import xml.etree.ElementTree as ET
import yaml
from io import StringIO
from typing import Dict, List, Any, Optional, Union
from rest_framework import renderers
from rest_framework.utils import encoders
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str


class ProxyExportError(Exception):
    """Custom exception for proxy export errors"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class BaseProxyRenderer(renderers.BaseRenderer):
    """
    Base renderer class with common functionality for proxy exports.
    
    Provides shared validation, error handling, field selection,
    and filtering capabilities for all proxy export formats.
    """
    
    # Default fields to include in exports
    DEFAULT_FIELDS = [
        'ip', 'port', 'proxy_type', 'country', 'city', 
        'is_working', 'response_time', 'created_at'
    ]
    
    # Available proxy fields for selection
    AVAILABLE_FIELDS = [
        'id', 'ip', 'port', 'proxy_type', 'tier', 'source_name',
        'username', 'password', 'country', 'country_code', 'region',
        'city', 'timezone', 'location_display', 'is_working',
        'last_checked', 'response_time', 'success_count', 'failure_count',
        'success_rate', 'created_at', 'updated_at', 'proxy_url', 'proxy_with_auth'
    ]
    
    def __init__(self):
        super().__init__()
        self.export_config = {}
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Main render method that handles common preprocessing.
        Subclasses should override render_data() instead.
        """
        if renderer_context is None:
            renderer_context = {}
        
        # Extract export configuration from request
        request = renderer_context.get('request')
        if request:
            self.export_config = self._extract_export_config(request)
        
        try:
            # Validate and preprocess data
            processed_data = self._preprocess_data(data)
            
            # Apply field selection
            filtered_data = self._apply_field_selection(processed_data)
            
            # Validate data quality
            validated_data = self._validate_data_quality(filtered_data)
            
            # Render the data in the specific format
            return self.render_data(validated_data, renderer_context)
            
        except Exception as e:
            if isinstance(e, ProxyExportError):
                raise e
            else:
                raise ProxyExportError(
                    message=f"Export rendering failed: {str(e)}",
                    error_code="RENDER_ERROR",
                    details={"original_error": str(e)}
                )
    
    def render_data(self, data: List[Dict], renderer_context: Dict) -> bytes:
        """
        Render the preprocessed data in the specific format.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement render_data()")
    
    def _extract_export_config(self, request) -> Dict:
        """Extract export configuration from request parameters"""
        config = {}
        
        # Field selection
        fields_param = request.query_params.get('fields')
        if fields_param:
            config['fields'] = [f.strip() for f in fields_param.split(',')]
        else:
            config['fields'] = self.DEFAULT_FIELDS.copy()
        
        # Format-specific options
        config['options'] = {}
        for key, value in request.query_params.items():
            if key.startswith('option_'):
                option_name = key[7:]  # Remove 'option_' prefix
                config['options'][option_name] = value
        
        return config
    
    def _preprocess_data(self, data) -> List[Dict]:
        """Preprocess and normalize the input data"""
        if not data:
            return []
        
        # Handle both single objects and lists
        if isinstance(data, dict):
            if 'results' in data:
                # Paginated response
                data_list = data['results']
            else:
                # Single object
                data_list = [data]
        elif isinstance(data, list):
            data_list = data
        else:
            raise ProxyExportError(
                message="Invalid data format for export",
                error_code="INVALID_DATA_FORMAT",
                details={"data_type": type(data).__name__}
            )
        
        return data_list
    
    def _apply_field_selection(self, data: List[Dict]) -> List[Dict]:
        """Apply field selection based on configuration"""
        selected_fields = self.export_config.get('fields', self.DEFAULT_FIELDS)
        
        # Validate selected fields
        invalid_fields = [f for f in selected_fields if f not in self.AVAILABLE_FIELDS]
        if invalid_fields:
            raise ProxyExportError(
                message="Invalid fields specified for export",
                error_code="INVALID_FIELDS",
                details={"invalid_fields": invalid_fields, "available_fields": self.AVAILABLE_FIELDS}
            )
        
        # Filter data to include only selected fields
        filtered_data = []
        for item in data:
            filtered_item = {}
            for field in selected_fields:
                if field in item:
                    filtered_item[field] = item[field]
                else:
                    # Handle missing fields gracefully
                    filtered_item[field] = None
            filtered_data.append(filtered_item)
        
        return filtered_data
    
    def _validate_data_quality(self, data: List[Dict]) -> List[Dict]:
        """Validate and clean proxy data quality"""
        validated_data = []
        invalid_count = 0
        
        for item in data:
            try:
                validated_item = self._validate_single_proxy(item)
                validated_data.append(validated_item)
            except ValidationError as e:
                invalid_count += 1
                # Handle invalid data based on configuration
                if self.export_config.get('options', {}).get('exclude_invalid', 'true').lower() == 'true':
                    continue  # Skip invalid entries
                else:
                    # Mark invalid entries clearly
                    item['_validation_error'] = str(e)
                    validated_data.append(item)
        
        # Log validation results if there were issues
        if invalid_count > 0:
            print(f"Export validation: {invalid_count} invalid entries processed")
        
        return validated_data
    
    def _validate_single_proxy(self, proxy_data: Dict) -> Dict:
        """Validate a single proxy entry"""
        validated = proxy_data.copy()
        
        # Validate IP address format if present
        if 'ip' in validated and validated['ip']:
            ip = validated['ip']
            if not self._is_valid_ip(ip):
                raise ValidationError(f"Invalid IP address: {ip}")
        
        # Validate port number if present
        if 'port' in validated and validated['port']:
            port = validated['port']
            try:
                port_int = int(port)
                if not (1 <= port_int <= 65535):
                    raise ValidationError(f"Invalid port number: {port}")
                validated['port'] = port_int
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid port format: {port}")
        
        # Validate proxy type if present
        if 'proxy_type' in validated and validated['proxy_type']:
            proxy_type = validated['proxy_type'].lower()
            valid_types = ['http', 'https', 'socks4', 'socks5']
            if proxy_type not in valid_types:
                raise ValidationError(f"Invalid proxy type: {proxy_type}")
            validated['proxy_type'] = proxy_type
        
        # Format proxy URLs if needed
        if 'ip' in validated and 'port' in validated and 'proxy_type' in validated:
            if 'proxy_url' not in validated or not validated['proxy_url']:
                validated['proxy_url'] = f"{validated['proxy_type']}://{validated['ip']}:{validated['port']}"
            
            # Generate authenticated URL if credentials are available
            if ('username' in validated and 'password' in validated and 
                validated['username'] and validated['password']):
                if 'proxy_with_auth' not in validated or not validated['proxy_with_auth']:
                    validated['proxy_with_auth'] = (
                        f"{validated['proxy_type']}://{validated['username']}:"
                        f"{validated['password']}@{validated['ip']}:{validated['port']}"
                    )
        
        return validated
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format (IPv4 or IPv6)"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _get_filename_timestamp(self) -> str:
        """Generate timestamp for filenames"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _generate_filename(self, base_name: str, extension: str, filters: Optional[Dict] = None) -> str:
        """Generate descriptive filename for export"""
        timestamp = self._get_filename_timestamp()
        filename_parts = [base_name, timestamp]
        
        # Add filter information to filename if available
        if filters:
            filter_parts = []
            if filters.get('proxy_type'):
                filter_parts.append(f"type-{filters['proxy_type']}")
            if filters.get('country'):
                filter_parts.append(f"country-{filters['country'][:3]}")  # First 3 chars
            if filters.get('is_working') is not None:
                status = "working" if filters['is_working'] else "all"
                filter_parts.append(f"status-{status}")
            
            if filter_parts:
                filename_parts.append("_".join(filter_parts))
        
        filename = "_".join(filename_parts) + f".{extension}"
        # Clean filename of invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename


class JSONProxyRenderer(BaseProxyRenderer):
    """
    JSON renderer for proxy exports with configuration options.
    
    Supports pretty-printing, minification, and structured JSON output
    with all requested proxy fields.
    """
    
    media_type = 'application/json'
    format = 'json'
    charset = 'utf-8'
    
    def render_data(self, data: List[Dict], renderer_context: Dict) -> bytes:
        """Render proxy data as JSON with configuration options"""
        options = self.export_config.get('options', {})
        
        # Determine JSON formatting options
        indent = None
        separators = (',', ':')  # Compact by default
        
        if options.get('pretty_print', 'false').lower() == 'true':
            indent = int(options.get('indent', 2))
            separators = (',', ': ')  # Pretty separators
        elif options.get('minify', 'false').lower() == 'true':
            # Ensure minimal whitespace
            separators = (',', ':')
            indent = None
        
        # Sort keys option
        sort_keys = options.get('sort_keys', 'false').lower() == 'true'
        
        # Structure option - wrap in metadata if requested
        include_metadata = options.get('include_metadata', 'false').lower() == 'true'
        
        if include_metadata:
            # Add export metadata
            export_data = {
                'metadata': {
                    'export_timestamp': self._get_current_timestamp(),
                    'total_records': len(data),
                    'format': 'json',
                    'fields': self.export_config.get('fields', self.DEFAULT_FIELDS),
                    'options': options
                },
                'proxies': data
            }
        else:
            export_data = data
        
        try:
            json_string = json.dumps(
                export_data,
                indent=indent,
                separators=separators,
                sort_keys=sort_keys,
                ensure_ascii=False,
                cls=encoders.JSONEncoder
            )
            return json_string.encode(self.charset)
            
        except (TypeError, ValueError) as e:
            raise ProxyExportError(
                message=f"JSON serialization failed: {str(e)}",
                error_code="JSON_SERIALIZATION_ERROR",
                details={"original_error": str(e)}
            )
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

class CSVProxyRenderer(BaseProxyRenderer):
    """
    CSV renderer for proxy exports with custom delimiters and formatting.
    
    Supports configurable delimiter, quote character, header generation,
    and proper CSV escaping for all proxy data fields.
    """
    
    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'
    
    def render_data(self, data: List[Dict], renderer_context: Dict) -> bytes:
        """Render proxy data as CSV with configuration options"""
        if not data:
            return b''
        
        options = self.export_config.get('options', {})
        
        # CSV formatting options
        delimiter = options.get('delimiter', ',')
        quote_char = options.get('quote_char', '"')
        include_headers = options.get('include_headers', 'true').lower() == 'true'
        line_terminator = options.get('line_terminator', '\n')
        
        # Validate delimiter and quote character
        if len(delimiter) != 1:
            raise ProxyExportError(
                message="CSV delimiter must be a single character",
                error_code="INVALID_CSV_DELIMITER",
                details={"delimiter": delimiter}
            )
        
        if len(quote_char) != 1:
            raise ProxyExportError(
                message="CSV quote character must be a single character",
                error_code="INVALID_CSV_QUOTE_CHAR",
                details={"quote_char": quote_char}
            )
        
        try:
            output = StringIO()
            
            # Get field names from the first record or configuration
            if data:
                fieldnames = list(data[0].keys())
            else:
                fieldnames = self.export_config.get('fields', self.DEFAULT_FIELDS)
            
            # Create CSV writer with custom options
            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
                delimiter=delimiter,
                quotechar=quote_char,
                quoting=csv.QUOTE_MINIMAL,
                lineterminator=line_terminator,
                extrasaction='ignore'  # Ignore extra fields not in fieldnames
            )
            
            # Write headers if requested
            if include_headers:
                # Option to customize header names
                header_mapping = options.get('header_mapping', {})
                if header_mapping:
                    custom_headers = {}
                    for field in fieldnames:
                        custom_headers[field] = header_mapping.get(field, field)
                    writer.writerow(custom_headers)
                else:
                    writer.writeheader()
            
            # Write data rows
            for row in data:
                # Clean and format row data for CSV
                cleaned_row = self._clean_csv_row(row)
                writer.writerow(cleaned_row)
            
            csv_content = output.getvalue()
            output.close()
            
            return csv_content.encode(self.charset)
            
        except Exception as e:
            raise ProxyExportError(
                message=f"CSV generation failed: {str(e)}",
                error_code="CSV_GENERATION_ERROR",
                details={"original_error": str(e)}
            )
    
    def _clean_csv_row(self, row: Dict) -> Dict:
        """Clean and format row data for CSV output"""
        cleaned = {}
        
        for key, value in row.items():
            if value is None:
                cleaned[key] = ''
            elif isinstance(value, bool):
                cleaned[key] = 'true' if value else 'false'
            elif isinstance(value, (list, dict)):
                # Convert complex types to JSON strings
                cleaned[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, str):
                # Clean string values - remove problematic characters
                cleaned[key] = value.replace('\n', ' ').replace('\r', ' ')
            else:
                cleaned[key] = str(value)
        
        return cleaned