from typing import List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, selectinload
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.future import select
import os
from dotenv import load_dotenv


load_dotenv()

db_config = {
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "host": os.getenv('DB_HOST'),
    "database": os.getenv('DB_DATABASE'),
}

DATABASE_URL = (f"postgresql+asyncpg://"
                f"{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Customer(Base):
    __tablename__ = 'myapp_customer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    orders = relationship('Order', back_populates='customer')


class Product(Base):
    __tablename__ = 'myapp_product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)


class Order(Base):
    __tablename__ = 'myapp_order'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('myapp_customer.id'))
    created_at = Column(DateTime)
    customer = relationship('Customer', back_populates='orders')
    products = relationship('OrderProduct', back_populates='order')


class OrderProduct(Base):
    __tablename__ = 'myapp_order_products'

    order_id = Column(Integer, ForeignKey('myapp_order.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('myapp_product.id'), primary_key=True)
    order = relationship('Order', back_populates='products')
    product = relationship('Product')


class CustomerSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True
        from_attributes = True


class ProductSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True
        from_attributes = True


class OrderSchema(BaseModel):
    id: int
    customer_id: int
    created_at: str  # Change this to str to handle datetime
    customer: CustomerSchema

    class Config:
        orm_mode = True
        from_attributes = True


class CombinedData(BaseModel):
    order: OrderSchema
    products: List[ProductSchema]


app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


async def get_db():
    async with async_session() as session:
        yield session


@app.get("/api/orders/{order_id}/", response_model=CombinedData)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.customer), selectinload(Order.products))
            .where(Order.id == order_id)
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        product_result = await session.execute(
            select(Product)
            .join(OrderProduct, OrderProduct.product_id == Product.id)
            .where(OrderProduct.order_id == order_id)
        )
        products = product_result.scalars().all()

        order_data = OrderSchema(
            id=order.id,
            customer_id=order.customer_id,
            created_at=order.created_at.isoformat() if order.created_at else None,
            customer=CustomerSchema.from_orm(order.customer)
        )
        products_data = [ProductSchema.from_orm(product) for product in products]

        combined_data = CombinedData(order=order_data, products=products_data)

        return combined_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
