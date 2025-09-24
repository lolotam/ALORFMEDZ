"""
Comprehensive Query Patterns for Hospital Pharmacy Management System
Defines all possible query patterns for every database table and operation type
"""

from typing import Dict, List

class ComprehensivePatterns:
    """Comprehensive query patterns for all database operations"""
    
    def __init__(self):
        self.patterns = self._build_comprehensive_patterns()
        self.clarification_options = self._build_clarification_options()
    
    def _build_comprehensive_patterns(self) -> Dict[str, List[str]]:
        """Build comprehensive patterns for all database queries"""
        return {
            # MEDICINES QUERIES
            'medicines_count': [
                r'how many medicines',
                r'total number of medicines',
                r'medicine count',
                r'count of medicines',
                r'number of medicines',
                r'total medicines'
            ],
            'medicines_list': [
                r'list all medicines',
                r'show all medicines',
                r'give me all medicine names',
                r'what medicines do we have',
                r'complete medicine list',
                r'all medicines in database'
            ],
            'medicines_by_category': [
                r'medicines by category',
                r'group medicines by category',
                r'medicine categories',
                r'categorize medicines',
                r'medicines in each category'
            ],
            'medicines_by_supplier': [
                r'medicines by supplier',
                r'which medicines from supplier',
                r'supplier medicines',
                r'medicines per supplier',
                r'group medicines by supplier'
            ],
            'medicines_stock_levels': [
                r'medicine stock levels',
                r'current stock of medicines',
                r'inventory levels',
                r'stock status of medicines',
                r'medicine quantities'
            ],
            'medicines_low_stock': [
                r'low stock medicines',
                r'medicines running out',
                r'medicines below limit',
                r'shortage medicines',
                r'medicines need restocking'
            ],
            'medicines_out_of_stock': [
                r'out of stock medicines',
                r'medicines with zero stock',
                r'empty stock medicines',
                r'unavailable medicines',
                r'medicines not in stock'
            ],
            'medicines_highest_stock': [
                r'highest stock medicines',
                r'medicines with most stock',
                r'maximum stock medicines',
                r'medicines with highest inventory',
                r'top stock medicines'
            ],
            'medicines_by_form': [
                r'medicines by form',
                r'tablets vs capsules',
                r'medicine forms',
                r'dosage forms',
                r'group by form dosage'
            ],
            'medicines_analysis': [
                r'comprehensive medicine analysis',
                r'complete medicine overview',
                r'medicine statistics',
                r'medicine summary report',
                r'analyze medicine data'
            ],
            
            # PATIENTS QUERIES
            'patients_count': [
                r'how many patients',
                r'total number of patients',
                r'patient count',
                r'count of patients',
                r'number of patients',
                r'total patients'
            ],
            'patients_list': [
                r'list all patients',
                r'show all patients',
                r'give me all patient names',
                r'what patients do we have',
                r'complete patient list',
                r'all patients in database'
            ],
            'patients_by_department': [
                r'patients by department',
                r'which patients in department',
                r'department patients',
                r'patients per department',
                r'group patients by department'
            ],
            'patients_by_gender': [
                r'patients by gender',
                r'male vs female patients',
                r'gender distribution',
                r'how many male patients',
                r'how many female patients'
            ],
            'patients_by_age': [
                r'patients by age',
                r'age distribution',
                r'oldest patients',
                r'youngest patients',
                r'average patient age'
            ],
            'patients_with_allergies': [
                r'patients with allergies',
                r'allergy information',
                r'patients allergic to',
                r'allergy list',
                r'patients with medical conditions'
            ],
            'patients_consumption': [
                r'patient consumption patterns',
                r'which patient consumed most',
                r'top consuming patients',
                r'patient medicine usage',
                r'consumption by patient'
            ],
            'patients_recent': [
                r'recent patients',
                r'new patients',
                r'patients added recently',
                r'latest patient registrations',
                r'recent admissions'
            ],
            'patients_analysis': [
                r'comprehensive patient analysis',
                r'complete patient overview',
                r'patient statistics',
                r'patient summary report',
                r'analyze patient data'
            ],
            
            # SUPPLIERS QUERIES
            'suppliers_count': [
                r'how many suppliers',
                r'total number of suppliers',
                r'supplier count',
                r'count of suppliers',
                r'number of suppliers',
                r'total suppliers'
            ],
            'suppliers_list': [
                r'list all suppliers',
                r'show all suppliers',
                r'give me all supplier names',
                r'what suppliers do we have',
                r'complete supplier list',
                r'all suppliers in database'
            ],
            'suppliers_by_type': [
                r'suppliers by type',
                r'medicine suppliers',
                r'equipment suppliers',
                r'supplier categories',
                r'group suppliers by type'
            ],
            'suppliers_performance': [
                r'supplier performance',
                r'best suppliers',
                r'top suppliers',
                r'supplier ratings',
                r'supplier quality metrics'
            ],
            'suppliers_contact_info': [
                r'supplier contact information',
                r'supplier phone numbers',
                r'supplier addresses',
                r'how to contact suppliers',
                r'supplier details'
            ],
            'suppliers_purchase_history': [
                r'supplier purchase history',
                r'purchases from supplier',
                r'supplier order history',
                r'what we bought from supplier',
                r'supplier transaction history'
            ],
            'suppliers_analysis': [
                r'comprehensive supplier analysis',
                r'complete supplier overview',
                r'supplier statistics',
                r'supplier summary report',
                r'analyze supplier data'
            ],
            
            # DEPARTMENTS QUERIES
            'departments_count': [
                r'how many departments',
                r'total number of departments',
                r'department count',
                r'count of departments',
                r'number of departments',
                r'total departments'
            ],
            'departments_list': [
                r'list all departments',
                r'show all departments',
                r'give me all department names',
                r'what departments do we have',
                r'complete department list',
                r'all departments in database'
            ],
            'departments_staff': [
                r'department staff',
                r'who runs each department',
                r'department managers',
                r'responsible persons',
                r'department contacts'
            ],
            'departments_inventory': [
                r'department inventory',
                r'stock by department',
                r'department stock levels',
                r'inventory per department',
                r'what each department has'
            ],
            'departments_consumption': [
                r'department consumption',
                r'which department uses most',
                r'consumption by department',
                r'department usage patterns',
                r'medicine usage per department'
            ],
            'departments_analysis': [
                r'comprehensive department analysis',
                r'complete department overview',
                r'department statistics',
                r'department summary report',
                r'analyze department data'
            ],

            # STORES QUERIES
            'stores_count': [
                r'how many stores',
                r'total number of stores',
                r'store count',
                r'count of stores',
                r'number of storage locations',
                r'total stores'
            ],
            'stores_list': [
                r'list all stores',
                r'show all storage locations',
                r'give me all store names',
                r'what stores do we have',
                r'complete store list',
                r'all stores in database'
            ],
            'stores_inventory': [
                r'store inventory',
                r'inventory by store',
                r'what is in each store',
                r'store stock levels',
                r'storage inventory'
            ],
            'stores_capacity': [
                r'store capacity',
                r'storage capacity',
                r'how much can stores hold',
                r'store limits',
                r'maximum storage'
            ],
            'stores_by_department': [
                r'stores by department',
                r'which stores belong to department',
                r'department storage locations',
                r'stores per department',
                r'departmental stores'
            ],
            'stores_analysis': [
                r'comprehensive store analysis',
                r'complete store overview',
                r'store statistics',
                r'store summary report',
                r'analyze store data'
            ],

            # PURCHASES QUERIES
            'purchases_count': [
                r'how many purchases',
                r'total number of purchases',
                r'purchase count',
                r'count of purchases',
                r'number of orders',
                r'total purchases'
            ],
            'purchases_list': [
                r'list all purchases',
                r'show all orders',
                r'give me purchase history',
                r'what purchases were made',
                r'complete purchase list',
                r'all purchases in database'
            ],
            'purchases_recent': [
                r'recent purchases',
                r'latest purchases',
                r'new orders',
                r'purchases this month',
                r'recent orders'
            ],
            'purchases_by_supplier': [
                r'purchases by supplier',
                r'orders from supplier',
                r'what we bought from',
                r'supplier purchase history',
                r'purchases per supplier'
            ],
            'purchases_expensive': [
                r'expensive purchases',
                r'highest cost purchases',
                r'most expensive orders',
                r'costly purchases',
                r'big purchases'
            ],
            'purchases_total_cost': [
                r'total purchase cost',
                r'how much spent on purchases',
                r'purchase expenses',
                r'total money spent',
                r'purchase budget'
            ],
            'purchases_by_date': [
                r'purchases by date',
                r'orders by month',
                r'purchase timeline',
                r'when were purchases made',
                r'purchase dates'
            ],
            'purchases_analysis': [
                r'comprehensive purchase analysis',
                r'complete purchase overview',
                r'purchase statistics',
                r'purchase summary report',
                r'analyze purchase data'
            ],

            # CONSUMPTION QUERIES
            'consumption_count': [
                r'how many consumption records',
                r'total consumption entries',
                r'consumption count',
                r'number of consumptions',
                r'usage records'
            ],
            'consumption_list': [
                r'list all consumption',
                r'show all usage',
                r'give me consumption history',
                r'what was consumed',
                r'complete consumption list'
            ],
            'consumption_by_patient': [
                r'consumption by patient',
                r'what patient consumed',
                r'patient usage',
                r'medicine taken by patient',
                r'consumption per patient'
            ],
            'consumption_by_medicine': [
                r'consumption by medicine',
                r'which medicine consumed most',
                r'medicine usage',
                r'most used medicines',
                r'consumption per medicine'
            ],
            'consumption_by_department': [
                r'consumption by department',
                r'department usage',
                r'which department uses most',
                r'consumption per department',
                r'departmental consumption'
            ],
            'consumption_recent': [
                r'recent consumption',
                r'latest usage',
                r'consumption this month',
                r'recent medicine usage',
                r'new consumption records'
            ],
            'consumption_trends': [
                r'consumption trends',
                r'usage patterns',
                r'consumption over time',
                r'usage statistics',
                r'consumption analysis'
            ],
            'consumption_analysis': [
                r'comprehensive consumption analysis',
                r'complete consumption overview',
                r'consumption statistics',
                r'consumption summary report',
                r'analyze consumption data'
            ],

            # TRANSFERS QUERIES
            'transfers_count': [
                r'how many transfers',
                r'total number of transfers',
                r'transfer count',
                r'count of transfers',
                r'number of transfers'
            ],
            'transfers_list': [
                r'list all transfers',
                r'show all transfers',
                r'give me transfer history',
                r'what transfers were made',
                r'complete transfer list'
            ],
            'transfers_recent': [
                r'recent transfers',
                r'latest transfers',
                r'new transfers',
                r'transfers this month',
                r'recent movements'
            ],
            'transfers_by_department': [
                r'transfers by department',
                r'department transfers',
                r'transfers from department',
                r'transfers to department',
                r'departmental transfers'
            ],
            'transfers_pending': [
                r'pending transfers',
                r'transfers waiting approval',
                r'unapproved transfers',
                r'transfers in progress',
                r'incomplete transfers'
            ],
            'transfers_routes': [
                r'transfer routes',
                r'common transfer paths',
                r'where transfers go',
                r'transfer destinations',
                r'transfer patterns'
            ],
            'transfers_analysis': [
                r'comprehensive transfer analysis',
                r'complete transfer overview',
                r'transfer statistics',
                r'transfer summary report',
                r'analyze transfer data'
            ],

            # GENERAL QUERIES
            'database_overview': [
                r'complete database overview',
                r'show everything',
                r'full system analysis',
                r'comprehensive overview',
                r'all data summary'
            ],
            'help_query': [
                r'help',
                r'what can you do',
                r'available commands',
                r'how to use',
                r'instructions'
            ]
        }
    
    def _build_clarification_options(self) -> Dict[str, Dict[str, str]]:
        """Build clarification options for ambiguous queries"""
        return {
            'medicines': {
                'a': 'List all medicine names',
                'b': 'Show medicine stock levels',
                'c': 'Analyze medicines by category',
                'd': 'Show low stock medicines',
                'e': 'Complete medicine analysis',
                'f': 'Something else'
            },
            'patients': {
                'a': 'List all patient names',
                'b': 'Show patients by department',
                'c': 'Analyze patient consumption',
                'd': 'Show patient demographics',
                'e': 'Complete patient analysis',
                'f': 'Something else'
            },
            'suppliers': {
                'a': 'List all supplier names',
                'b': 'Show supplier contact info',
                'c': 'Analyze supplier performance',
                'd': 'Show purchase history',
                'e': 'Complete supplier analysis',
                'f': 'Something else'
            },
            'departments': {
                'a': 'List all department names',
                'b': 'Show department staff',
                'c': 'Analyze department inventory',
                'd': 'Show department consumption',
                'e': 'Complete department analysis',
                'f': 'Something else'
            },
            'stores': {
                'a': 'List all storage locations',
                'b': 'Show inventory by store',
                'c': 'Analyze storage capacity',
                'd': 'Show store assignments',
                'e': 'Complete store analysis',
                'f': 'Something else'
            },
            'purchases': {
                'a': 'List recent purchases',
                'b': 'Show purchase costs',
                'c': 'Analyze purchase trends',
                'd': 'Show expensive purchases',
                'e': 'Complete purchase analysis',
                'f': 'Something else'
            },
            'consumption': {
                'a': 'List recent consumption',
                'b': 'Show consumption by patient',
                'c': 'Analyze consumption patterns',
                'd': 'Show high consumption items',
                'e': 'Complete consumption analysis',
                'f': 'Something else'
            },
            'transfers': {
                'a': 'List recent transfers',
                'b': 'Show transfer routes',
                'c': 'Analyze transfer patterns',
                'd': 'Show pending transfers',
                'e': 'Complete transfer analysis',
                'f': 'Something else'
            }
        }
    
    def get_patterns(self) -> Dict[str, List[str]]:
        """Get all command patterns"""
        return self.patterns
    
    def get_clarification_options(self, entity_type: str) -> Dict[str, str]:
        """Get clarification options for a specific entity type"""
        return self.clarification_options.get(entity_type, {})
    
    def get_all_entity_types(self) -> List[str]:
        """Get all supported entity types"""
        return list(self.clarification_options.keys())

# Global instance
comprehensive_patterns = ComprehensivePatterns()
