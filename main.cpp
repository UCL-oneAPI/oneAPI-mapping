/*BHEADER****************************************************************
 * (c) 2007   The Regents of the University of California               *
 *                                                                      *
 * See the file COPYRIGHT_and_DISCLAIMER for a complete copyright       *
 * notice and disclaimer.                                               *
 *                                                                      *
 *EHEADER****************************************************************/

//--------------
//  A micro kernel 
//--------------
#include <CL/sycl.hpp>
#include <dpct/dpct.hpp>

#ifdef _OPENMP
#include <omp.h>
#else
#endif

#include "headers.h"
#include <cmath>

// CUDA/HIP block size or OpenCL work-group size
#define BLOCK_SIZE 256

// 
const int testIter   = 500;
double totalWallTime = 0.0;

// 
void test_Matvec();
void test_Relax();
void test_Axpy();

//
int main(int argc, char *argv[])
{
#ifdef _OPENMP
  double t0        = 0.0,
         t1        = 0.0,
#else
  printf("**** Warning: OpenMP is disabled ****\n");
#endif

  double del_wtime = 0.0;

#ifdef _OPENMP
  int  max_num_threads;
#endif


  printf("\n");
  printf("//------------ \n");
  printf("// \n");
  printf("//  CORAL  AMGmk Benchmark Version 1.0 \n");
  printf("// \n");
  printf("//------------ \n");

  printf("\n testIter   = %d \n\n", testIter );  

 
#ifdef _OPENMP
  printf("\n testIter   = %d \n\n", testIter );  
  #pragma omp parallel
     #pragma omp master
        max_num_threads = omp_get_num_threads();
   printf("\nmax_num_threads = %d \n\n",max_num_threads );
#endif


#ifdef _OPENMP
  t0 = omp_get_wtime();
#else
  auto t0 = std::chrono::steady_clock::now();
#endif

  // Matvec
  totalWallTime = 0.0;
 
  test_Matvec();

  printf("\n");
  printf("//------------ \n");
  printf("// \n");
  printf("//   MATVEC\n");
  printf("// \n");
  printf("//------------ \n");

  printf("\nWall time = %f seconds. \n", totalWallTime);


  // Relax
  totalWallTime = 0.0;

  test_Relax();

  printf("\n");
  printf("//------------ \n");
  printf("// \n");
  printf("//   Relax\n");
  printf("// \n");
  printf("//------------ \n");

  printf("\nWall time = %f seconds. \n", totalWallTime);


  // Axpy
  totalWallTime = 0.0;
 
  test_Axpy();

  printf("\n");
  printf("//------------ \n");
  printf("// \n");
  printf("//   Axpy\n");
  printf("// \n");
  printf("//------------ \n");

  printf("\nWall time = %f seconds. \n", totalWallTime);

#ifdef _OPENMP
  t1 = omp_get_wtime();
  del_wtime = t1 - t0;
#else
  auto t1 = std::chrono::steady_clock::now();
  std::chrono::duration<double> diff = t1 - t0;
  del_wtime = diff.count();
#endif


  printf("\nTotal Wall time = %f seconds. \n", del_wtime);

  return  0;
}

void test_Matvec()
{
#ifdef _OPENMP
  double t0 = 0.0,
         t1 = 0.0;
#endif

  hypre_CSRMatrix *A;
  hypre_Vector *x, *y, *sol;
  int nx, ny, nz, i;
  double *values;
  double *y_data, *sol_data;
  double error, diff;

  nx = 50;  /* size per proc nx*ny*nz */
  ny = 50;
  nz = 50;

  values = hypre_CTAlloc(double, 4);
  values[0] = 6; 
  values[1] = -1;
  values[2] = -1;
  values[3] = -1;

  A = GenerateSeqLaplacian(nx, ny, nz, values, &y, &x, &sol);

  hypre_SeqVectorSetConstantValues(x,1);
  hypre_SeqVectorSetConstantValues(y,0);

#ifdef _OPENMP
  t0 = omp_get_wtime();
#else
  auto t0 = std::chrono::steady_clock::now();
#endif

  for (i=0; i<testIter; ++i)
      hypre_CSRMatrixMatvec(1,A,x,0,y);

#ifdef _OPENMP
  t1 = omp_get_wtime() ;
  totalWallTime += t1 - t0;
#else
  auto t1 = std::chrono::steady_clock::now();
  std::chrono::duration<double> tdiff = t1 - t0;
  totalWallTime += tdiff.count();
#endif

 
  y_data = hypre_VectorData(y);
  sol_data = hypre_VectorData(sol);

  error = 0;
  for (i=0; i < nx*ny*nz; i++)
  {
      diff = fabs(y_data[i] - sol_data[i]);
      if (diff > error) error = diff;
  }
     
  if (error > 0) printf(" \n Matvec: error: %e\n", error);

  hypre_TFree(values);
  hypre_CSRMatrixDestroy(A);
  hypre_SeqVectorDestroy(x);
  hypre_SeqVectorDestroy(y);
  hypre_SeqVectorDestroy(sol);

}

void
relax (const double *A_diag_data, const int *A_diag_i, const int *A_diag_j, 
             double *u_data, const double *f_data, const int n,
             sycl::nd_item<3> item_ct1)
{
   int i = item_ct1.get_local_range().get(2) * item_ct1.get_group(2) +
           item_ct1.get_local_id(2);
    if (i >= n) return;

    /*-----------------------------------------------------------
     * If diagonal is nonzero, relax point i; otherwise, skip it.
     *-----------------------------------------------------------*/

    if ( A_diag_data[A_diag_i[i]] != 0.0)
    {
      double res = f_data[i];
      for (int jj = A_diag_i[i]+1; jj < A_diag_i[i+1]; jj++)
      {
        int ii = A_diag_j[jj];
        res -= A_diag_data[jj] * u_data[ii];
      }
      u_data[i] = res / A_diag_data[A_diag_i[i]];
    }
}

void test_Relax()
{
   dpct::device_ext &dev_ct1 = dpct::get_current_device();
   sycl::queue &q_ct1 = dev_ct1.default_queue();
#ifdef _OPENMP
  double t0 = 0.0,
         t1 = 0.0;
#endif

  hypre_CSRMatrix *A;
  hypre_Vector *x, *y, *sol;
  int nx, ny, nz, i;
  double *values;
  double diff, error;

  nx = 50;  /* size per proc nx*ny*nz */
  ny = 50;
  nz = 50;

  values = hypre_CTAlloc(double, 4);
  values[0] = 6; 
  values[1] = -1;
  values[2] = -1;
  values[3] = -1;

  A = GenerateSeqLaplacian(nx, ny, nz, values, &y, &x, &sol);

  hypre_SeqVectorSetConstantValues(x,1);

#ifdef _OPENMP
  t0 = omp_get_wtime();
#else
  auto t0 = std::chrono::steady_clock::now();
#endif

  double         *A_diag_data  = hypre_CSRMatrixData(A);
  int            *A_diag_i     = hypre_CSRMatrixI(A);
  int            *A_diag_j     = hypre_CSRMatrixJ(A);

  int             n       = hypre_CSRMatrixNumRows(A);
  int             nonzero = hypre_CSRMatrixNumNonzeros(A);

  double         *u_data  = hypre_VectorData(x);
  //int         u_data_size  = hypre_VectorSize(x);

  double         *f_data  = hypre_VectorData(sol);
  //int         f_data_size  = hypre_VectorSize(sol);

  int             grid_size = nx*ny*nz;
  double         *d_A_diag_data;
  int            *d_A_diag_i;
  int            *d_A_diag_j;
  double         *d_u_data;
  double         *d_f_data;

   d_A_diag_data = sycl::malloc_device<double>(nonzero, q_ct1);
   d_A_diag_i = sycl::malloc_device<int>((grid_size + 1), q_ct1);
   d_A_diag_j = sycl::malloc_device<int>(nonzero, q_ct1);
   d_u_data = sycl::malloc_device<double>(grid_size, q_ct1);
   d_f_data = sycl::malloc_device<double>(grid_size, q_ct1);

   q_ct1.memcpy(d_A_diag_data, A_diag_data, sizeof(double) * nonzero).wait();
   q_ct1.memcpy(d_A_diag_i, A_diag_i, sizeof(int) * (grid_size + 1)).wait();
   q_ct1.memcpy(d_A_diag_j, A_diag_j, sizeof(int) * nonzero).wait();
   q_ct1.memcpy(d_u_data, u_data, sizeof(double) * grid_size).wait();
   q_ct1.memcpy(d_f_data, f_data, sizeof(double) * grid_size).wait();

   sycl::range<3> block1D(BLOCK_SIZE, 1, 1);
   sycl::range<3> grid1D((n + BLOCK_SIZE - 1) / BLOCK_SIZE, 1, 1);

  for (i=0; i<testIter; ++i) {
      q_ct1.submit([&](sycl::handler &cgh) {
         auto dpct_global_range =
             sycl::range<3>(grid1D) * sycl::range<3>(block1D);
         auto dpct_local_range = sycl::range<3>(block1D);

         cgh.parallel_for(
             sycl::nd_range<3>(sycl::range<3>(dpct_global_range.get(2),
                                              dpct_global_range.get(1),
                                              dpct_global_range.get(0)),
                               sycl::range<3>(dpct_local_range.get(2),
                                              dpct_local_range.get(1),
                                              dpct_local_range.get(0))),
             [=](sycl::nd_item<3> item_ct1) {
                relax(d_A_diag_data, d_A_diag_i, d_A_diag_j, d_u_data, d_f_data,
                      n, item_ct1);
             });
      });
  }

   q_ct1.memcpy(u_data, d_u_data, sizeof(double) * grid_size).wait();

   sycl::free(d_A_diag_data, q_ct1);
   sycl::free(d_A_diag_i, q_ct1);
   sycl::free(d_A_diag_j, q_ct1);
   sycl::free(d_u_data, q_ct1);
   sycl::free(d_f_data, q_ct1);

#ifdef _OPENMP
  t1 = omp_get_wtime();
  totalWallTime += t1 - t0;
#else
  auto t1 = std::chrono::steady_clock::now();
  std::chrono::duration<double> tdiff = t1 - t0;
  totalWallTime += tdiff.count();
#endif

  error = 0;
  for (i=0; i < nx*ny*nz; i++)
  {
      diff = fabs(u_data[i] - 1);
      if (diff > error) error = diff;
  }
     
  if (error > 0) printf(" \n Relax: error: %e\n", error);

  hypre_TFree(values);
  hypre_CSRMatrixDestroy(A);
  hypre_SeqVectorDestroy(x);
  hypre_SeqVectorDestroy(y);
  hypre_SeqVectorDestroy(sol);

}

void test_Axpy()
{
#ifdef _OPENMP
  double t0 = 0.0,
         t1 = 0.0;
#endif


  hypre_Vector *x, *y;
  int nx, i;
  double alpha=0.5;
  double diff, error;
  double *y_data;

  nx = 125000;  /* size per proc  */

  x = hypre_SeqVectorCreate(nx);
  y = hypre_SeqVectorCreate(nx);

  hypre_SeqVectorInitialize(x);
  hypre_SeqVectorInitialize(y);

  hypre_SeqVectorSetConstantValues(x,1);
  hypre_SeqVectorSetConstantValues(y,1);

 
#ifdef _OPENMP
  t0 = omp_get_wtime();
#else
  auto t0 = std::chrono::steady_clock::now();
#endif

  for (i=0; i<testIter; ++i)
      hypre_SeqVectorAxpy(alpha,x,y);
#ifdef _OPENMP
  t1 = omp_get_wtime();
#else
  auto t1 = std::chrono::steady_clock::now();
#endif
  

  y_data = hypre_VectorData(y);
  error = 0;
  for (i=0; i < nx; i++)
  {
      diff = fabs(y_data[i] - 1 - 0.5 * (double)testIter);
      if (diff > error) error = diff;
  }
     
  if (error > 0) printf(" \n Axpy: error: %e\n", error);

#ifdef _OPENMP
  totalWallTime += t1 - t0; 
#else
  std::chrono::duration<double> tdiff = t1 - t0;
  totalWallTime += tdiff.count();
#endif

  hypre_SeqVectorDestroy(x);
  hypre_SeqVectorDestroy(y);

}
