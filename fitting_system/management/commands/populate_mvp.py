from django.core.management.base import BaseCommand
from fitting_system.models import Size, Color, Product, ProductVariant, Inventory


class Command(BaseCommand):
    help = 'Populate database with MVP data - minimal clothing sets for men and women'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing products...')
        # Clear existing data
        Inventory.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        
        self.stdout.write('Populating database with MVP data...')
        
        # Ensure Sizes exist
        self.stdout.write('Ensuring sizes exist...')
        sizes_data = [
            {'name': 'S', 'chest_min': 85, 'chest_max': 92, 'waist_min': 70, 'waist_max': 77, 
             'shoulder_min': 40, 'shoulder_max': 43, 'height_min': 160, 'height_max': 170},
            {'name': 'M', 'chest_min': 93, 'chest_max': 100, 'waist_min': 78, 'waist_max': 85, 
             'shoulder_min': 44, 'shoulder_max': 47, 'height_min': 168, 'height_max': 178},
            {'name': 'L', 'chest_min': 101, 'chest_max': 108, 'waist_min': 86, 'waist_max': 93, 
             'shoulder_min': 48, 'shoulder_max': 51, 'height_min': 175, 'height_max': 185},
            {'name': 'XL', 'chest_min': 109, 'chest_max': 116, 'waist_min': 94, 'waist_max': 101, 
             'shoulder_min': 52, 'shoulder_max': 55, 'height_min': 180, 'height_max': 190},
        ]
        
        for size_data in sizes_data:
            Size.objects.get_or_create(name=size_data['name'], defaults=size_data)
        
        # Ensure Colors exist
        self.stdout.write('Ensuring colors exist...')
        colors_data = [
            # Neutral colors for MVP
            {'name': 'Black', 'hex_code': '#000000', 'category': 'neutral'},
            {'name': 'White', 'hex_code': '#FFFFFF', 'category': 'neutral'},
            {'name': 'Navy Blue', 'hex_code': '#000080', 'category': 'neutral'},
            {'name': 'Gray', 'hex_code': '#808080', 'category': 'neutral'},
            {'name': 'Beige', 'hex_code': '#F5F5DC', 'category': 'neutral'},
            
            # Additional colors
            {'name': 'Burgundy', 'hex_code': '#800020', 'category': 'medium'},
            {'name': 'Light Blue', 'hex_code': '#ADD8E6', 'category': 'light'},
            {'name': 'Pastel Pink', 'hex_code': '#FFD1DC', 'category': 'light'},
        ]
        
        for color_data in colors_data:
            Color.objects.get_or_create(name=color_data['name'], defaults=color_data)
        
        # Create MVP Products - Only 6 essential items
        self.stdout.write('Creating MVP products...')
        products_data = [
            # Men's Set (3 items)
            {'name': 'Classic Cotton Shirt', 'category': 'shirt', 'fit_type': 'regular', 'gender': 'men', 
             'price': 49.99, 'description': 'A timeless classic cotton shirt perfect for any occasion. Made from 100% premium cotton for maximum comfort and breathability.'},
            
            {'name': 'Casual Denim Jeans', 'category': 'pants', 'fit_type': 'regular', 'gender': 'men', 
             'price': 79.99, 'description': 'Comfortable denim jeans with a classic fit. Durable and stylish for everyday wear with premium denim fabric.'},
            
            {'name': 'Leather Jacket', 'category': 'jacket', 'fit_type': 'regular', 'gender': 'men', 
             'price': 199.99, 'description': 'Premium leather jacket with a classic design. Timeless piece that never goes out of style, crafted from genuine leather.'},
            
            # Women's Set (3 items)
            {'name': 'Elegant Blouse', 'category': 'shirt', 'fit_type': 'regular', 'gender': 'women', 
             'price': 54.99, 'description': 'Sophisticated blouse with delicate details. Perfect for both office and evening wear with premium silk-like fabric.'},
            
            {'name': 'Summer Dress', 'category': 'dress', 'fit_type': 'regular', 'gender': 'women', 
             'price': 89.99, 'description': 'Light and breezy summer dress perfect for warm weather. Comfortable and stylish with a flattering silhouette.'},
            
            {'name': 'High-Waist Trousers', 'category': 'pants', 'fit_type': 'regular', 'gender': 'women', 
             'price': 74.99, 'description': 'Flattering high-waist trousers with a comfortable fit. Versatile for any occasion from office to casual outings.'},
        ]
        
        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            products.append(product)
            if created:
                self.stdout.write(f'  Created: {product.name}')
        
        # Create Product Variants and Inventory
        self.stdout.write('Creating product variants and inventory...')
        sizes = Size.objects.all()
        colors = Color.objects.all()[:5]  # Use first 5 colors
        
        for product in products:
            # Create variants for each product
            product_sizes = list(sizes)[:3]  # S, M, L
            product_colors = list(colors)[:3]  # First 3 colors
            
            counter = 1
            for size in product_sizes:
                for color in product_colors:
                    sku = f"{product.id}-{size.name}-{color.id}-{counter}"
                    variant, created = ProductVariant.objects.get_or_create(
                        product=product,
                        size=size,
                        color=color,
                        defaults={'sku': sku}
                    )
                    counter += 1
                    
                    # Create inventory for this variant with varied stock levels
                    if created:
                        # Track variant count for distribution
                        variant_count = Inventory.objects.count()
                        
                        # Distribute stock: first 10 out of stock, next 10 low stock, rest in stock
                        if variant_count < 10:
                            # Out of stock (0 quantity)
                            quantity = 0
                        elif variant_count < 20:
                            # Low stock (1-4 quantity, threshold is 5)
                            import random
                            quantity = random.randint(1, 4)
                        else:
                            # In stock (10-25 quantity)
                            import random
                            quantity = random.randint(10, 25)
                        
                        Inventory.objects.create(
                            product_variant=variant,
                            quantity=quantity,
                            low_stock_threshold=5
                        )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully populated MVP database!'))
        self.stdout.write(f'📦 Created {Product.objects.count()} products (3 men\'s + 3 women\'s)')
        self.stdout.write(f'📏 Using {Size.objects.count()} sizes')
        self.stdout.write(f'🎨 Using {Color.objects.count()} colors')
        self.stdout.write(f'🏷️  Created {ProductVariant.objects.count()} product variants')
        self.stdout.write(f'📊 Created {Inventory.objects.count()} inventory records')
        
        # Display product summary
        self.stdout.write('\n📋 MVP Product Summary:')
        self.stdout.write('  Men\'s Set:')
        for product in Product.objects.filter(gender='men'):
            self.stdout.write(f'    • {product.name} ({product.category})')
        self.stdout.write('  Women\'s Set:')
        for product in Product.objects.filter(gender='women'):
            self.stdout.write(f'    • {product.name} ({product.category})')
